"""
Send all charts in flawed_charts/ to Kimi K2.6 for visualization flaw analysis.
Results are saved one record per line, joined with metadata on (flaw_category, chart_name).

Images are uploaded once to the Kimi Files API and reused across runs.
The mapping from chart to file_id is cached in results/kimi/image_ids.json.

USAGE
-----
From the project root (dataset_evaluation/):

    source venv/bin/activate

    # --- Synchronous mode (one request at a time) ---

    # All charts:
    python3 send_to_models/evaluate_kimi.py

    # One flaw category:
    python3 send_to_models/evaluate_kimi.py --flawtype indistinguishable_colors

    # One specific chart:
    python3 send_to_models/evaluate_kimi.py --flawtype indistinguishable_colors --chartname line_chart_2

    # Multiple repetitions per chart:
    python3 send_to_models/evaluate_kimi.py --runs 3

    # Resume an interrupted run:
    python3 send_to_models/evaluate_kimi.py --resume results/kimi/sync/20260428_143012.jsonl

    # --- Batch mode (async, 100 MB input limit) ---

    # Submit a batch job (all charts, or scoped with --flawtype / --chartname):
    python3 send_to_models/evaluate_kimi.py --batch
    python3 send_to_models/evaluate_kimi.py --batch --flawtype indistinguishable_colors --runs 3

    # Check batch status:
    python3 send_to_models/evaluate_kimi.py --batch-status batch_abc123

    # Collect results once the batch is complete:
    python3 send_to_models/evaluate_kimi.py --batch-collect batch_abc123

Each synchronous run creates a timestamped output file:
    results/kimi/sync/YYYYMMDD_HHMMSS.jsonl

Batch jobs are stored under:
    results/kimi/batches/<batch_id>/meta.json        <- created on submit
    results/kimi/batches/<batch_id>/results.jsonl    <- created on collect

REQUIREMENTS
------------
- .env file in the project root containing: KIMI_API_KEY=<your key>
- Python packages: openai, python-dotenv  (already installed in venv)

IMAGE REUSE
-----------
Images are uploaded once to the Kimi Files API (purpose="image") and cached in
results/kimi/image_ids.json. Subsequent runs reuse the same file_ids, referenced
via ms://<file_id> in every request — keeping batch JSONL files small.

OUTPUT FORMAT
-------------
Each line in the .jsonl file is a JSON object with these fields:
    run_id          — timestamp string (sync) or batch id (batch)
    timestamp       — ISO-8601 UTC time of the individual request
    model           — model used (kimi-k2.6)
    flaw_category   — subdirectory name under flawed_charts/ (e.g. "truncated_axis")
    chart_name      — PNG filename without extension (e.g. "bar_chart_3")
    repetition      — which repeat this is (1-indexed)
    prompt          — the exact prompt sent to the model
    response_text   — the model's plain-text response
    usage           — dict with prompt_tokens, completion_tokens, total_tokens
"""

import argparse
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

api_key = os.environ.get("KIMI_API_KEY")
if not api_key:
    sys.exit("KIMI_API_KEY not found in environment or .env file")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.ai/v1",
)

FLAWED_CHARTS = Path(__file__).parent.parent / "flawed_charts"
RESULTS_ROOT = Path(__file__).parent.parent / "results"
SYNC_DIR = RESULTS_ROOT / "kimi" / "sync"
BATCHES_DIR = RESULTS_ROOT / "kimi" / "batches"
IMAGE_IDS_FILE = RESULTS_ROOT / "kimi" / "image_ids.json"
MODEL = "kimi-k2.6"
PROMPT = "Evaluate this chart."

BATCH_INPUT_LIMIT_BYTES = 100 * 1024 * 1024  # 100 MB


# ---------------------------------------------------------------------------
# Image upload cache
# ---------------------------------------------------------------------------

def load_image_ids() -> dict[str, str]:
    """Load the cached chart → file_id mapping from disk."""
    if IMAGE_IDS_FILE.exists():
        with open(IMAGE_IDS_FILE) as f:
            return json.load(f)
    return {}


def save_image_ids(cache: dict[str, str]) -> None:
    IMAGE_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IMAGE_IDS_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def image_cache_key(flaw_category: str, chart_name: str) -> str:
    return f"{flaw_category}/{chart_name}"


def ensure_uploaded(flaw_category: str, chart_name: str, png_path: Path, cache: dict[str, str]) -> str:
    """Upload the image if not already cached; return the file_id."""
    key = image_cache_key(flaw_category, chart_name)
    if key in cache:
        return cache[key]

    print(f"  [upload] {flaw_category}/{chart_name}...")
    with open(png_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="image")
    cache[key] = file_obj.id
    save_image_ids(cache)
    return file_obj.id


def upload_all_images(png_files: list[Path]) -> dict[str, str]:
    """Upload all images that aren't already cached; returns the full cache."""
    cache = load_image_ids()
    needed = [
        p for p in png_files
        if image_cache_key(p.parent.parent.name, p.stem) not in cache
    ]

    if not needed:
        print(f"All {len(png_files)} image(s) already uploaded — reusing cached file_ids.")
        return cache

    print(f"Uploading {len(needed)} new image(s) (of {len(png_files)} total)...")
    for png_path in needed:
        flaw_category = png_path.parent.parent.name
        chart_name = png_path.stem
        ensure_uploaded(flaw_category, chart_name, png_path, cache)

    print(f"Upload complete. Cache: {IMAGE_IDS_FILE}\n")
    return cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    usage_prompt: int | None,
    usage_completion: int | None,
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
            "prompt_tokens": usage_prompt,
            "completion_tokens": usage_completion,
            "total_tokens": usage_total,
        },
    }


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
    cache: dict[str, str],
) -> None:
    file_id = ensure_uploaded(flaw_category, chart_name, png_path, cache)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"ms://{file_id}"}},
                        {"type": "text", "text": PROMPT},
                    ],
                }
            ],
            extra_body={"thinking": {"type": "disabled"}},
        )

        usage = response.usage
        record = make_record(
            run_id, flaw_category, chart_name, repetition,
            response.choices[0].message.content,
            usage.prompt_tokens if usage else None,
            usage.completion_tokens if usage else None,
            usage.total_tokens if usage else None,
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        token_info = (
            f"prompt={usage.prompt_tokens} completion={usage.completion_tokens}"
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

    cache = upload_all_images(png_files)

    done_counts = load_completed(out_path)
    already_done = sum(done_counts.values())
    if already_done:
        print(f"Resuming — {already_done} request(s) already done\n")

    for png_path in png_files:
        flaw_category = png_path.parent.parent.name
        chart_name = png_path.stem
        done = done_counts.get((flaw_category, chart_name), 0)

        for rep in range(done + 1, args.runs + 1):
            process_chart_sync(run_id, flaw_category, chart_name, rep, png_path, out_path, cache)


# ---------------------------------------------------------------------------
# Batch mode — submit
# ---------------------------------------------------------------------------

def run_batch_submit(args: argparse.Namespace) -> None:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)

    png_files = collect_png_files(args)
    if not png_files:
        sys.exit("No charts found for the given arguments.")

    total_requests = len(png_files) * args.runs

    # Upload all images first so we have file_ids
    print(f"Ensuring all {len(png_files)} image(s) are uploaded...")
    cache = upload_all_images(png_files)

    print(f"Building batch input for {len(png_files)} chart(s) × {args.runs} run(s) = {total_requests} request(s)...")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, prefix="kimi_batch_input_"
    ) as tmp:
        tmp_path = Path(tmp.name)
        for png_path in png_files:
            flaw_category = png_path.parent.parent.name
            chart_name = png_path.stem
            file_id = cache[image_cache_key(flaw_category, chart_name)]

            for rep in range(1, args.runs + 1):
                request = {
                    "custom_id": custom_id(flaw_category, chart_name, rep),
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image_url", "image_url": {"url": f"ms://{file_id}"}},
                                    {"type": "text", "text": PROMPT},
                                ],
                            }
                        ],
                        "thinking": {"type": "disabled"},
                    },
                }
                tmp.write(json.dumps(request) + "\n")

    file_size = tmp_path.stat().st_size
    print(f"Batch input file: {tmp_path} ({file_size / 1024 / 1024:.1f} MB)")

    if file_size > BATCH_INPUT_LIMIT_BYTES:
        tmp_path.unlink()
        sys.exit(
            f"Batch input file exceeds the 100 MB Kimi limit ({file_size / 1024 / 1024:.1f} MB). "
            "Use --flawtype to submit smaller batches."
        )

    print("Uploading batch input file...")
    with open(tmp_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="batch")
    tmp_path.unlink()
    print(f"Uploaded file ID: {uploaded.id}")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"charts": str(len(png_files)), "model": MODEL},
    )

    print(f"\nBatch submitted successfully.")
    print(f"Batch ID : {batch.id}")
    print(f"Status   : {batch.status}")

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
            {"flaw_category": p.parent.parent.name, "chart_name": p.stem}
            for p in png_files
        ],
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Metadata : {meta_path}")
    print(f"\nCheck status with:")
    print(f"  python3 send_to_models/evaluate_kimi.py --batch-status {batch.id}")


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
        print(f"  python3 send_to_models/evaluate_kimi.py --batch-collect {batch_id}")


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
        except (ValueError, IndexError):
            print(f"[WARN] Could not parse custom_id: {cid!r}")
            continue

        # Kimi returns status_code 0 for successful batch responses (not 200)
        status_code = response.get("status_code") if response else None
        if error or not response or status_code not in (0, 200):
            err_msg = error or response
            print(f"[ERR]  {flaw_category}/{chart_name} rep {repetition} — {err_msg}")
            errors += 1
            continue

        body = response.get("body", {})
        try:
            response_text = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            response_text = None

        usage = body.get("usage", {})
        record = make_record(
            batch_id, flaw_category, chart_name, repetition,
            response_text,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            usage.get("total_tokens"),
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        saved += 1

    print(f"\nDone. Saved {saved} records, {errors} errors.")
    print(f"Output : {out_path}")

    if batch.error_file_id:
        print(f"\nSome requests failed — error file: {batch.error_file_id}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate charts with Kimi K2.6.")

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
