"""
Send all charts in flawed_charts/ to Gemini Flash for visualization flaw analysis.
Results are saved one record per line, joined with metadata on (flaw_category, chart_name).

USAGE
-----
From the project root (dataset_evaluation/):

    source venv/bin/activate

    # --- Synchronous mode (one request at a time) ---

    # All charts:
    python3 send_to_models/evaluate_gemini_flash.py

    # One flaw category:
    python3 send_to_models/evaluate_gemini_flash.py --flawtype indistinguishable_colors

    # One specific chart:
    python3 send_to_models/evaluate_gemini_flash.py --flawtype indistinguishable_colors --chartname line_chart_2

    # Multiple repetitions per chart:
    python3 send_to_models/evaluate_gemini_flash.py --runs 3

    # Resume an interrupted run:
    python3 send_to_models/evaluate_gemini_flash.py --resume results/gemini_flash/sync/20260428_143012.jsonl

    # --- Batch mode (50% cheaper, async, up to 24h turnaround) ---

    # Submit a batch job (all charts, or scoped with --flawtype / --chartname):
    python3 send_to_models/evaluate_gemini_flash.py --batch
    python3 send_to_models/evaluate_gemini_flash.py --batch --flawtype indistinguishable_colors --runs 3

    # Check batch status:
    python3 send_to_models/evaluate_gemini_flash.py --batch-status batches/123456789

    # Collect results once the batch is complete:
    python3 send_to_models/evaluate_gemini_flash.py --batch-collect batches/123456789

Each synchronous run creates a timestamped output file:
    results/gemini_flash/sync/YYYYMMDD_HHMMSS.jsonl

Batch jobs are stored under:
    results/gemini_flash/batches/<job_id>/meta.json        ← created on submit
    results/gemini_flash/batches/<job_id>/results.jsonl    ← created on collect

REQUIREMENTS
------------
- .env file in the project root containing: GEMINI_API_KEY=<your key>
- Python packages: google-genai, python-dotenv  (pip install google-genai python-dotenv)

IMAGE RESOLUTION
----------------
Using MEDIA_RESOLUTION_HIGH (1120 tokens/image) — recommended for detailed chart analysis.
Switch to MEDIA_RESOLUTION_MEDIUM (560 tokens) to halve image costs at some quality loss.

OUTPUT FORMAT
-------------
Each line in the .jsonl file is a JSON object with these fields:
    run_id          — timestamp string (sync) or batch job id (batch)
    timestamp       — ISO-8601 UTC time of the individual request
    model           — model used
    flaw_category   — subdirectory name under flawed_charts/ (e.g. "truncated_axis")
    chart_name      — PNG filename without extension (e.g. "bar_chart_3")
    repetition      — which repeat this is (1-indexed)
    prompt          — the exact prompt sent to the model
    response_text   — the model's plain-text response
    usage           — dict with prompt_token_count, candidates_token_count, total_token_count
"""

import argparse
import base64
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("google-genai not installed. Run: pip install google-genai")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit("GEMINI_API_KEY not found in environment or .env file")

client = genai.Client(api_key=api_key)

FLAWED_CHARTS = Path(__file__).parent.parent / "flawed_charts"
RESULTS_ROOT = Path(__file__).parent.parent / "results"
SYNC_DIR = RESULTS_ROOT / "gemini_flash" / "sync"
BATCHES_DIR = RESULTS_ROOT / "gemini_flash" / "batches"
MODEL = "gemini-3-flash-preview"
PROMPT = "Evaluate this chart."
MIME_TYPE = "image/png"

TERMINAL_STATES = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
BATCH_FILE_LIMIT_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def batch_key(flaw_category: str, chart_name: str, repetition: int) -> str:
    return f"{flaw_category}||{chart_name}||{repetition}"


def parse_batch_key(key: str) -> tuple[str, str, int]:
    parts = key.split("||")
    flaw_category, chart_name = parts[0], parts[1]
    repetition = int(parts[2]) if len(parts) > 2 else 1
    return flaw_category, chart_name, repetition


def job_folder_name(job_name: str) -> str:
    """Convert 'batches/123456789' to a safe folder name 'batches_123456789'."""
    return job_name.replace("/", "_")


def collect_png_files(args: argparse.Namespace) -> list[Path]:
    if args.flawtype and args.chartname:
        return sorted(FLAWED_CHARTS.glob(f"{args.flawtype}/png/{args.chartname}.png"))
    elif args.flawtype:
        return sorted(FLAWED_CHARTS.glob(f"{args.flawtype}/png/*.png"))
    else:
        return sorted(FLAWED_CHARTS.glob("*/png/*.png"))


def load_completed(out_path: Path) -> dict[tuple[str, str], int]:
    """Return how many times each (flaw_category, chart_name) pair has been recorded."""
    counts: dict[tuple[str, str], int] = {}
    if out_path.exists():
        with open(out_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    key = (record["flaw_category"], record["chart_name"])
                    counts[key] = counts.get(key, 0) + 1
    return counts


def make_record(
    run_id: str,
    flaw_category: str,
    chart_name: str,
    repetition: int,
    response_text: str | None,
    usage: dict | None,
) -> dict:
    return {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "flaw_category": flaw_category,
        "chart_name": chart_name,
        "repetition": repetition,
        "prompt": PROMPT,
        "response_text": response_text,
        "usage": usage or {},
    }


def extract_usage(response) -> dict:
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return {}
    return {
        "prompt_token_count": getattr(meta, "prompt_token_count", None),
        "candidates_token_count": getattr(meta, "candidates_token_count", None),
        "total_token_count": getattr(meta, "total_token_count", None),
    }


def extract_usage_from_dict(usage_dict: dict) -> dict:
    return {
        "prompt_token_count": usage_dict.get("promptTokenCount"),
        "candidates_token_count": usage_dict.get("candidatesTokenCount"),
        "total_token_count": usage_dict.get("totalTokenCount"),
    }


def extract_text_from_response_dict(resp: dict) -> str | None:
    try:
        return resp["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Synchronous mode
# ---------------------------------------------------------------------------

def process_chart_sync(
    run_id: str,
    flaw_category: str,
    chart_name: str,
    repetition: int,
    png_path: Path,
    out_path: Path,
) -> None:
    image_bytes = png_path.read_bytes()

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=MIME_TYPE),
                PROMPT,
            ],
            config=types.GenerateContentConfig(
                media_resolution=types.MediaResolution.MEDIA_RESOLUTION_HIGH,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL,
                ),
            ),
        )

        record = make_record(
            run_id, flaw_category, chart_name, repetition,
            response.text,
            extract_usage(response),
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        usage = record["usage"]
        token_info = (
            f"prompt={usage.get('prompt_token_count')} out={usage.get('candidates_token_count')}"
            if usage else "usage=unknown"
        )
        rep_label = f" [rep {repetition}]" if repetition > 1 else ""
        print(f"[OK]   {flaw_category}/{chart_name}{rep_label} — {token_info}")

    except Exception as e:
        print(f"[ERR]  {flaw_category}/{chart_name} — {type(e).__name__}: {e}")


def run_sync(args: argparse.Namespace) -> None:
    SYNC_DIR.mkdir(parents=True, exist_ok=True)

    if args.resume:
        out_path = Path(args.resume)
        if not out_path.exists():
            sys.exit(f"File not found: {out_path}")
        run_id = out_path.stem
        print(f"Resuming run {run_id} from {out_path}")
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = SYNC_DIR / f"{run_id}.jsonl"

    png_files = collect_png_files(args)
    if not png_files:
        sys.exit("No charts found for the given arguments.")

    total_requests = len(png_files) * args.runs
    print(f"Found {len(png_files)} chart(s) × {args.runs} run(s) = {total_requests} request(s)")
    print(f"Run ID : {run_id}")
    print(f"Output : {out_path}\n")

    done_counts = load_completed(out_path)
    already_done = sum(done_counts.values())
    if already_done:
        print(f"Resuming — {already_done} request(s) already done\n")

    for png_path in png_files:
        flaw_category = png_path.parent.parent.name
        chart_name = png_path.stem
        done = done_counts.get((flaw_category, chart_name), 0)

        for rep in range(done + 1, args.runs + 1):
            process_chart_sync(run_id, flaw_category, chart_name, rep, png_path, out_path)


# ---------------------------------------------------------------------------
# Batch mode — submit
# ---------------------------------------------------------------------------

def run_batch_submit(args: argparse.Namespace) -> None:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)

    png_files = collect_png_files(args)
    if not png_files:
        sys.exit("No charts found for the given arguments.")

    total_requests = len(png_files) * args.runs
    print(f"Building batch input for {len(png_files)} chart(s) × {args.runs} run(s) = {total_requests} request(s)...")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, prefix="gemini_batch_input_"
    ) as tmp:
        tmp_path = Path(tmp.name)
        for png_path in png_files:
            flaw_category = png_path.parent.parent.name
            chart_name = png_path.stem
            image_b64 = base64.standard_b64encode(png_path.read_bytes()).decode()

            for rep in range(1, args.runs + 1):
                entry = {
                    "key": batch_key(flaw_category, chart_name, rep),
                    "request": {
                        "contents": [{
                            "role": "user",
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": MIME_TYPE,
                                        "data": image_b64,
                                    }
                                },
                                {"text": PROMPT},
                            ],
                        }],
                        "generationConfig": {
                            "mediaResolution": "MEDIA_RESOLUTION_HIGH",
                        },
                    },
                }
                tmp.write(json.dumps(entry) + "\n")

    file_size = tmp_path.stat().st_size
    print(f"Batch input file: {tmp_path} ({file_size / 1024 / 1024:.1f} MB)")

    if file_size > BATCH_FILE_LIMIT_BYTES:
        tmp_path.unlink()
        sys.exit(
            f"Batch input file exceeds the 2 GB Gemini limit ({file_size / 1024 / 1024:.1f} MB). "
            "Use --flawtype to submit smaller batches."
        )

    print("Uploading batch input file to File API...")
    uploaded = client.files.upload(
        file=str(tmp_path),
        config=types.UploadFileConfig(
            display_name=f"gemini_flash_batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            mime_type="application/jsonl",
        ),
    )
    tmp_path.unlink()
    print(f"Uploaded file: {uploaded.name}")

    batch_job = client.batches.create(
        model=MODEL,
        src=uploaded.name,
        config={"display_name": f"chart_eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"},
    )

    print(f"\nBatch submitted successfully.")
    print(f"Job name : {batch_job.name}")
    print(f"State    : {batch_job.state.name}")

    folder_name = job_folder_name(batch_job.name)
    batch_dir = BATCHES_DIR / folder_name
    batch_dir.mkdir(parents=True, exist_ok=True)
    meta_path = batch_dir / "meta.json"

    meta = {
        "job_name": batch_job.name,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "prompt": PROMPT,
        "runs_per_chart": args.runs,
        "chart_count": len(png_files),
        "total_requests": total_requests,
        "charts": [
            {"flaw_category": p.parent.parent.name, "chart_name": p.stem}
            for p in png_files
        ],
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Metadata : {meta_path}")
    print(f"\nCheck status with:")
    print(f"  python3 send_to_models/evaluate_gemini_flash.py --batch-status {batch_job.name}")


# ---------------------------------------------------------------------------
# Batch mode — status
# ---------------------------------------------------------------------------

def run_batch_status(job_name: str) -> None:
    batch_job = client.batches.get(name=job_name)
    state = batch_job.state.name
    print(f"Job name : {batch_job.name}")
    print(f"State    : {state}")
    if hasattr(batch_job, "error") and batch_job.error:
        print(f"Error    : {batch_job.error}")
    if state == "JOB_STATE_SUCCEEDED":
        print(f"\nReady to collect. Run:")
        print(f"  python3 send_to_models/evaluate_gemini_flash.py --batch-collect {job_name}")


# ---------------------------------------------------------------------------
# Batch mode — collect
# ---------------------------------------------------------------------------

def run_batch_collect(job_name: str) -> None:
    batch_job = client.batches.get(name=job_name)
    state = batch_job.state.name

    if state != "JOB_STATE_SUCCEEDED":
        sys.exit(f"Batch is not complete yet (state: {state}). Try again later.")

    folder_name = job_folder_name(job_name)
    batch_dir = BATCHES_DIR / folder_name
    batch_dir.mkdir(parents=True, exist_ok=True)
    out_path = batch_dir / "results.jsonl"

    print(f"Downloading results for job {job_name}...")

    result_file_name = batch_job.dest.file_name
    raw_bytes = client.files.download(file=result_file_name)
    raw_text = raw_bytes.decode("utf-8")

    saved = 0
    errors = 0
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        entry = json.loads(line)
        key = entry.get("key", "")

        try:
            flaw_category, chart_name, repetition = parse_batch_key(key)
        except (ValueError, IndexError):
            print(f"[WARN] Could not parse key: {key!r}")
            continue

        # Check for error (status object instead of response)
        if "status" in entry and not entry.get("response"):
            print(f"[ERR]  {flaw_category}/{chart_name} rep {repetition} — {entry['status']}")
            errors += 1
            continue

        resp = entry.get("response", {})
        response_text = extract_text_from_response_dict(resp)
        usage = extract_usage_from_dict(resp.get("usageMetadata", {}))

        record = make_record(
            job_name, flaw_category, chart_name, repetition,
            response_text, usage,
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        saved += 1

    print(f"\nDone. Saved {saved} records, {errors} errors.")
    print(f"Output : {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate charts with Gemini Flash.")

    parser.add_argument(
        "--flawtype",
        help="Only process charts from this flaw category (e.g. indistinguishable_colors).",
    )
    parser.add_argument(
        "--chartname",
        help="Only process this specific chart (requires --flawtype, e.g. line_chart_2).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        metavar="N",
        help="How many times to send each chart-prompt pair (default: 1).",
    )
    parser.add_argument(
        "--resume",
        metavar="FILE",
        help="Path to an existing .jsonl run file to resume (sync mode only).",
    )

    batch_group = parser.add_mutually_exclusive_group()
    batch_group.add_argument(
        "--batch",
        action="store_true",
        help="Submit a batch job instead of running synchronously.",
    )
    batch_group.add_argument(
        "--batch-status",
        metavar="JOB_NAME",
        help="Check the status of a previously submitted batch (e.g. batches/123456789).",
    )
    batch_group.add_argument(
        "--batch-collect",
        metavar="JOB_NAME",
        help="Download and save results of a completed batch.",
    )

    args = parser.parse_args()

    if args.chartname and not args.flawtype:
        parser.error("--chartname requires --flawtype")
    if args.resume and args.batch:
        parser.error("--resume and --batch cannot be used together")

    return args


def main() -> None:
    args = parse_args()

    if args.batch_status:
        run_batch_status(args.batch_status)
    elif args.batch_collect:
        run_batch_collect(args.batch_collect)
    elif args.batch:
        run_batch_submit(args)
    else:
        run_sync(args)


if __name__ == "__main__":
    main()
