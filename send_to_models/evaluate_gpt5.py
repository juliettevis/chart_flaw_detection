"""
Send all charts in flawed_charts/ to GPT-5 for visualization flaw analysis.
Results are saved to results/gpt5_<run_id>.jsonl, one record per line.
Each record is self-contained and can be joined with metadata on (flaw_category, chart_name).

USAGE
-----
From the project root (dataset_evaluation/):

    source venv/bin/activate

    # --- Synchronous mode (one request at a time) ---

    # All charts:
    python3 send_to_models/evaluate_gpt5.py

    # One flaw category:
    python3 send_to_models/evaluate_gpt5.py --flawtype indistinguishable_colors

    # One specific chart:
    python3 send_to_models/evaluate_gpt5.py --flawtype indistinguishable_colors --chartname line_chart_2

    # Resume an interrupted run:
    python3 send_to_models/evaluate_gpt5.py --resume results/gpt5/sync/20260428_143012.jsonl

    # --- Batch mode (50% cheaper, async, up to 24h turnaround) ---

    # Submit a batch job (all charts, or scoped with --flawtype / --chartname):
    python3 send_to_models/evaluate_gpt5.py --batch
    python3 send_to_models/evaluate_gpt5.py --batch --flawtype indistinguishable_colors

    # Check batch status:
    python3 send_to_models/evaluate_gpt5.py --batch-status batch_abc123

    # Collect results once the batch is complete:
    python3 send_to_models/evaluate_gpt5.py --batch-collect batch_abc123

Each synchronous run creates a timestamped output file:
    results/gpt5/sync/YYYYMMDD_HHMMSS.jsonl

Batch jobs are stored under:
    results/gpt5/batches/<batch_id>/meta.json        ← created on submit
    results/gpt5/batches/<batch_id>/results.jsonl    ← created on collect

REQUIREMENTS
------------
- .env file in the project root containing: GPT_API_KEY=<your key>
- Python packages: openai, python-dotenv  (already installed in venv)

OUTPUT FORMAT
-------------
Each line in the .jsonl file is a JSON object with these fields:
    run_id          — timestamp string shared by all records in this run
    timestamp       — ISO-8601 UTC time of the individual request
    model           — model used (gpt-5)
    flaw_category   — subdirectory name under flawed_charts/ (e.g. "truncated_axis")
    chart_name      — PNG filename without extension (e.g. "bar_chart_3")
    prompt          — the exact prompt sent to the model
    response_text   — the model's plain-text response
    usage           — dict with input_tokens, output_tokens, total_tokens
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

import openai

api_key = os.environ.get("GPT_API_KEY")
if not api_key:
    sys.exit("GPT_API_KEY not found in environment or .env file")

client = openai.OpenAI(api_key=api_key)

FLAWED_CHARTS = Path(__file__).parent.parent / "flawed_charts"
RESULTS_ROOT = Path(__file__).parent.parent / "results"
SYNC_DIR = RESULTS_ROOT / "gpt5" / "sync"
BATCHES_DIR = RESULTS_ROOT / "gpt5" / "batches"
MODEL = "gpt-5.4"
PROMPT = "Evaluate this chart."

BATCH_INPUT_LIMIT_BYTES = 200 * 1024 * 1024  # 200 MB


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def custom_id(flaw_category: str, chart_name: str, repetition: int) -> str:
    return f"{flaw_category}||{chart_name}||{repetition}"


def parse_custom_id(cid: str) -> tuple[str, str, int]:
    parts = cid.split("||")
    flaw_category, chart_name = parts[0], parts[1]
    repetition = int(parts[2]) if len(parts) > 2 else 1
    return flaw_category, chart_name, repetition


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
    usage_input: int | None,
    usage_output: int | None,
    usage_total: int | None,
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
        "usage": {
            "input_tokens": usage_input,
            "output_tokens": usage_output,
            "total_tokens": usage_total,
        },
    }


def extract_text_from_batch_body(body: dict) -> str | None:
    """Extract response text from a raw /v1/responses batch result body."""
    for item in body.get("output", []):
        if item.get("type") == "message":
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    return block.get("text")
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
    image_b64 = encode_image(png_path)

    try:
        response = client.responses.create(
            model=MODEL,
            reasoning={"effort": "none"},
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image_b64}",
                            "detail":"original"
                        },
                        {"type": "input_text", "text": PROMPT},
                    ],
                }
            ],
            max_output_tokens=2048,
        )

        usage = response.usage
        record = make_record(
            run_id, flaw_category, chart_name, repetition,
            response.output_text,
            usage.input_tokens if usage else None,
            usage.output_tokens if usage else None,
            usage.total_tokens if usage else None,
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        token_info = (
            f"input={usage.input_tokens} output={usage.output_tokens}"
            if usage else "usage=unknown"
        )
        rep_label = f" [rep {repetition}]" if repetition > 1 else ""
        print(f"[OK]   {flaw_category}/{chart_name}{rep_label} — {token_info}")

    except openai.APIStatusError as e:
        print(f"[ERR]  {flaw_category}/{chart_name} — HTTP {e.status_code} — {e.message}")
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

    # Write batch input JSONL to a temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, prefix="gpt5_batch_input_"
    ) as tmp:
        tmp_path = Path(tmp.name)
        for png_path in png_files:
            flaw_category = png_path.parent.parent.name
            chart_name = png_path.stem
            image_b64 = encode_image(png_path)

            for rep in range(1, args.runs + 1):
                request = {
                    "custom_id": custom_id(flaw_category, chart_name, rep),
                    "method": "POST",
                    "url": "/v1/responses",
                    "body": {
                        "model": MODEL,
                        "reasoning": {"effort": "none"},
                        "max_output_tokens": 2048,
                        "input": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_image",
                                        "image_url": f"data:image/png;base64,{image_b64}",
                                        "detail":"original"
                                    },
                                    {"type": "input_text", "text": PROMPT},
                                ],
                            }
                        ],
                    },
                }
                tmp.write(json.dumps(request) + "\n")

    file_size = tmp_path.stat().st_size
    print(f"Batch input file: {tmp_path} ({file_size / 1024 / 1024:.1f} MB)")

    if file_size > BATCH_INPUT_LIMIT_BYTES:
        tmp_path.unlink()
        sys.exit(
            f"Batch input file exceeds the 200 MB OpenAI limit ({file_size / 1024 / 1024:.1f} MB). "
            "Use --flawtype to submit smaller batches."
        )

    # Upload to OpenAI
    print("Uploading batch input file...")
    with open(tmp_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="batch")
    tmp_path.unlink()
    print(f"Uploaded file ID: {uploaded.id}")

    # Create the batch
    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={"charts": str(len(png_files)), "model": MODEL},
    )
    print(f"\nBatch submitted successfully.")
    print(f"Batch ID : {batch.id}")
    print(f"Status   : {batch.status}")
    print(f"Expires  : {batch.expires_at}")

    # Save metadata locally so we can collect later
    batch_dir = BATCHES_DIR / batch.id
    batch_dir.mkdir(parents=True, exist_ok=True)
    meta_path = batch_dir / "meta.json"
    meta = {
        "batch_id": batch.id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "prompt": PROMPT,
        "runs_per_chart": args.runs,
        "chart_count": len(png_files),
        "total_requests": total_requests,
        "charts": [
            {
                "flaw_category": p.parent.parent.name,
                "chart_name": p.stem,
            }
            for p in png_files
        ],
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata : {meta_path}")
    print(f"\nCheck status with:")
    print(f"  python3 send_to_models/evaluate_gpt5.py --batch-status {batch.id}")


# ---------------------------------------------------------------------------
# Batch mode — status
# ---------------------------------------------------------------------------

def run_batch_status(batch_id: str) -> None:
    batch = client.batches.retrieve(batch_id)
    counts = batch.request_counts
    print(f"Batch ID  : {batch.id}")
    print(f"Status    : {batch.status}")
    print(f"Requests  : total={counts.total}  completed={counts.completed}  failed={counts.failed}")
    if batch.status == "completed":
        print(f"\nReady to collect. Run:")
        print(f"  python3 send_to_models/evaluate_gpt5.py --batch-collect {batch_id}")


# ---------------------------------------------------------------------------
# Batch mode — collect
# ---------------------------------------------------------------------------

def run_batch_collect(batch_id: str) -> None:
    batch = client.batches.retrieve(batch_id)
    if batch.status != "completed":
        sys.exit(f"Batch is not complete yet (status: {batch.status}). Try again later.")

    if not batch.output_file_id:
        sys.exit("Batch completed but output_file_id is missing.")

    batch_dir = BATCHES_DIR / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    out_path = batch_dir / "results.jsonl"

    print(f"Downloading results for batch {batch_id}...")
    raw_output = client.files.content(batch.output_file_id).text

    saved = 0
    errors = 0
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue

        result = json.loads(line)
        cid = result.get("custom_id", "")
        error = result.get("error")
        response = result.get("response", {})

        try:
            flaw_category, chart_name, repetition = parse_custom_id(cid)
        except ValueError:
            print(f"[WARN] Could not parse custom_id: {cid!r}")
            continue

        if error or not response or response.get("status_code") != 200:
            err_msg = error or response
            print(f"[ERR]  {flaw_category}/{chart_name} rep {repetition} — {err_msg}")
            errors += 1
            continue

        body = response.get("body", {})
        response_text = extract_text_from_batch_body(body)
        usage = body.get("usage", {})

        record = make_record(
            batch_id, flaw_category, chart_name, repetition,
            response_text,
            usage.get("input_tokens"),
            usage.get("output_tokens"),
            usage.get("total_tokens"),
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        saved += 1

    print(f"\nDone. Saved {saved} records, {errors} errors.")
    print(f"Output : {out_path}")

    if batch.error_file_id:
        print(f"\nSome requests failed — error file: {batch.error_file_id}")
        print("Download with: client.files.content('<error_file_id>').text")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate charts with GPT-5.")

    # Scope filters (apply to both sync and batch submit)
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

    # Sync-only
    parser.add_argument(
        "--resume",
        metavar="FILE",
        help="Path to an existing .jsonl run file to resume (sync mode only).",
    )

    # Batch actions (mutually exclusive)
    batch_group = parser.add_mutually_exclusive_group()
    batch_group.add_argument(
        "--batch",
        action="store_true",
        help="Submit a batch job instead of running synchronously.",
    )
    batch_group.add_argument(
        "--batch-status",
        metavar="BATCH_ID",
        help="Check the status of a previously submitted batch.",
    )
    batch_group.add_argument(
        "--batch-collect",
        metavar="BATCH_ID",
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
