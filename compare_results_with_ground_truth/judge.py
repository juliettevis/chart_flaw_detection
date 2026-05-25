"""
LLM-as-a-judge: evaluate model responses against ground-truth flaw metadata.

Uses Gemini Flash to assess whether a candidate response identifies the
planted visualization flaw in a chart, based on the evaluation rubric in
evaluation_prompt.md.

USAGE
-----
From the project root (dataset_evaluation/):

    source venv/bin/activate

    # --- Synchronous mode (one request at a time) ---

    # All collected batches for a model:
    python3 compare_results_with_ground_truth/judge.py --model kimi
    python3 compare_results_with_ground_truth/judge.py --model gemini_flash

    # One specific results file:
    python3 compare_results_with_ground_truth/judge.py --results results/kimi/batches/batch_xxx/results.jsonl

    # --- Batch mode (async, cheaper) ---

    # Submit:
    python3 compare_results_with_ground_truth/judge.py --model kimi --batch
    python3 compare_results_with_ground_truth/judge.py --results results/kimi/batches/batch_xxx/results.jsonl --batch

    # Check status:
    python3 compare_results_with_ground_truth/judge.py --batch-status batches/xyz

    # Collect:
    python3 compare_results_with_ground_truth/judge.py --batch-collect batches/xyz

OUTPUT
------
Sync / Collect:
    compare_results_with_ground_truth/results/<model>/judge_results.jsonl     (--model)
    compare_results_with_ground_truth/results/<batch_folder>/judge_results.jsonl  (--results)

Batch submissions are tracked under:
    compare_results_with_ground_truth/batches/<job_folder>/meta.json
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

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("google-genai not installed. Run: pip install google-genai")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit("GEMINI_API_KEY not found in environment or .env file")

client = genai.Client(api_key=api_key)

PROJECT_ROOT    = Path(__file__).parent.parent
FLAWED_CHARTS   = PROJECT_ROOT / "flawed_charts"
RESULTS_ROOT    = PROJECT_ROOT / "results"
JUDGE_DIR       = Path(__file__).parent
JUDGE_RESULTS   = JUDGE_DIR / "results"
JUDGE_BATCHES   = JUDGE_DIR / "batches"
PROMPT_TEMPLATE = JUDGE_DIR / "evaluation_prompt.md"

JUDGE_MODEL = "gemini-3-flash-preview"

# Schema used both for the Python SDK (sync) and the REST batch API.
# Gemini accepts uppercase type names in both contexts.
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "rationale": {"type": "STRING"},
        "target_flaw_prominence": {
            "type": "STRING",
            "enum": ["primary", "supporting", "incidental", "absent"],
        },
        "other_flaws_mentioned": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
    },
    "required": ["rationale", "target_flaw_prominence", "other_flaws_mentioned"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_template() -> str:
    return PROMPT_TEMPLATE.read_text()


def fill_prompt(template: str, flaw_type: str, flaw_description: str, candidate_response: str) -> str:
    return (
        template
        .replace("{{flaw_category}}", flaw_type)
        .replace("{{flaw_description}}", flaw_description)
        .replace("{{model_response}}", candidate_response)
    )


def load_metadata(flaw_category: str, chart_name: str) -> dict:
    path = FLAWED_CHARTS / flaw_category / "metadata" / f"{chart_name}.json"
    with open(path) as f:
        return json.load(f)


def load_results_file(path: Path) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def collect_source_files(args: argparse.Namespace) -> list[Path]:
    if args.results:
        return [Path(args.results)]
    return sorted((RESULTS_ROOT / args.model).glob("batches/*/results.jsonl"))


def infer_output_path(args: argparse.Namespace) -> Path:
    if args.results:
        p = Path(args.results)
        batch_folder = p.parent.name              # e.g. batches_efaca77...
        model_name   = p.parent.parent.parent.name  # e.g. gemini_flash
        return JUDGE_RESULTS / model_name / batch_folder / "judge_results.jsonl"
    return JUDGE_RESULTS / args.model / "judge_results.jsonl"


def job_folder_name(job_name: str) -> str:
    return job_name.replace("/", "_")


# Separator unlikely to appear in run_id, flaw_category, or chart_name.
_SEP = "|||"


def make_key(source_run_id: str, flaw_category: str, chart_name: str, repetition: int) -> str:
    return _SEP.join([source_run_id, flaw_category, chart_name, str(repetition)])


def parse_key(key: str) -> tuple[str, str, str, int]:
    parts = key.split(_SEP)
    return parts[0], parts[1], parts[2], int(parts[3])


def make_record(
    judge_run_id: str,
    evaluated_model: str,
    source_run_id: str,
    flaw_category: str,
    chart_name: str,
    repetition: int,
    flaw_type: str,
    flaw_description: str,
    candidate_response: str,
    verdict: dict,
    usage: dict,
) -> dict:
    return {
        "judge_run_id":            judge_run_id,
        "timestamp":               datetime.now(timezone.utc).isoformat(),
        "judge_model":             JUDGE_MODEL,
        "evaluated_model":         evaluated_model,
        "source_run_id":           source_run_id,
        "flaw_category":           flaw_category,
        "chart_name":              chart_name,
        "repetition":              repetition,
        "ground_truth_flaw_type":  flaw_type,
        "ground_truth_description": flaw_description,
        "candidate_response":      candidate_response,
        "target_flaw_prominence":  verdict.get("target_flaw_prominence"),
        "other_flaws_mentioned":   verdict.get("other_flaws_mentioned", []),
        "rationale":               verdict.get("rationale"),
        "usage":                   usage,
    }


def extract_usage_sdk(response) -> dict:
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return {}
    return {
        "prompt_token_count":      getattr(meta, "prompt_token_count", None),
        "candidates_token_count":  getattr(meta, "candidates_token_count", None),
        "total_token_count":       getattr(meta, "total_token_count", None),
    }


def extract_usage_batch(usage_dict: dict) -> dict:
    return {
        "prompt_token_count":      usage_dict.get("promptTokenCount"),
        "candidates_token_count":  usage_dict.get("candidatesTokenCount"),
        "total_token_count":       usage_dict.get("totalTokenCount"),
    }


# ---------------------------------------------------------------------------
# Synchronous mode
# ---------------------------------------------------------------------------

def run_sync(args: argparse.Namespace) -> None:
    template = load_template()
    source_files = collect_source_files(args)
    if not source_files:
        sys.exit("No results files found.")

    all_records: list[dict] = []
    for f in source_files:
        all_records.extend(load_results_file(f))

    out_path = infer_output_path(args)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    print(f"Loaded {len(all_records)} records from {len(source_files)} file(s)")
    print(f"Output : {out_path}\n")

    saved = errors = 0

    for rec in all_records:
        flaw_category     = rec["flaw_category"]
        chart_name        = rec["chart_name"]
        repetition        = rec.get("repetition", 1)
        source_run_id     = rec["run_id"]
        evaluated_model   = rec["model"]
        candidate_response = rec.get("response_text", "")

        try:
            meta = load_metadata(flaw_category, chart_name)
        except FileNotFoundError:
            print(f"[ERR]  {flaw_category}/{chart_name} — metadata not found")
            errors += 1
            continue

        flaw_type        = meta.get("flaw_type", flaw_category)
        flaw_description = meta.get("description", "")
        prompt           = fill_prompt(template, flaw_type, flaw_description, candidate_response)

        try:
            response = client.models.generate_content(
                model=JUDGE_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            verdict = json.loads(response.text)
            usage   = extract_usage_sdk(response)
        except Exception as e:
            print(f"[ERR]  {flaw_category}/{chart_name} rep {repetition} — {type(e).__name__}: {e}")
            errors += 1
            continue

        record = make_record(
            run_id, evaluated_model, source_run_id,
            flaw_category, chart_name, repetition,
            flaw_type, flaw_description, candidate_response,
            verdict, usage,
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        saved += 1

        run_label = source_run_id[:24]
        print(f"[OK]   {flaw_category}/{chart_name} rep {repetition} ({run_label}) — {verdict.get('target_flaw_prominence')}")

    print(f"\nDone. Saved {saved}, errors {errors}.")
    print(f"Output : {out_path}")


# ---------------------------------------------------------------------------
# Batch mode — submit
# ---------------------------------------------------------------------------

def run_batch_submit(args: argparse.Namespace) -> None:
    template = load_template()
    source_files = collect_source_files(args)
    if not source_files:
        sys.exit("No results files found.")

    all_records: list[dict] = []
    for f in source_files:
        all_records.extend(load_results_file(f))

    print(f"Building batch input for {len(all_records)} records from {len(source_files)} file(s)...")

    JUDGE_BATCHES.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, prefix="judge_batch_") as tmp:
        tmp_path = Path(tmp.name)
        skipped = 0
        for rec in all_records:
            flaw_category      = rec["flaw_category"]
            chart_name         = rec["chart_name"]
            repetition         = rec.get("repetition", 1)
            source_run_id      = rec["run_id"]
            candidate_response = rec.get("response_text", "")

            try:
                meta = load_metadata(flaw_category, chart_name)
            except FileNotFoundError:
                print(f"[WARN] Skipping {flaw_category}/{chart_name} — metadata not found")
                skipped += 1
                continue

            flaw_type        = meta.get("flaw_type", flaw_category)
            flaw_description = meta.get("description", "")
            prompt           = fill_prompt(template, flaw_type, flaw_description, candidate_response)

            entry = {
                "key": make_key(source_run_id, flaw_category, chart_name, repetition),
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": RESPONSE_SCHEMA,
                    },
                },
            }
            tmp.write(json.dumps(entry) + "\n")

    file_size = tmp_path.stat().st_size
    print(f"Batch input: {file_size / 1024 / 1024:.1f} MB  ({len(all_records) - skipped} entries)")

    print("Uploading to File API...")
    uploaded = client.files.upload(
        file=str(tmp_path),
        config=types.UploadFileConfig(
            display_name=f"judge_batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            mime_type="application/jsonl",
        ),
    )
    tmp_path.unlink()
    print(f"Uploaded: {uploaded.name}")

    batch_job = client.batches.create(
        model=JUDGE_MODEL,
        src=uploaded.name,
        config={"display_name": f"judge_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"},
    )

    print(f"\nBatch submitted: {batch_job.name}  state={batch_job.state.name}")

    folder    = job_folder_name(batch_job.name)
    batch_dir = JUDGE_BATCHES / folder
    batch_dir.mkdir(parents=True, exist_ok=True)

    out_path = infer_output_path(args)

    meta = {
        "job_name":        batch_job.name,
        "submitted_at":    datetime.now(timezone.utc).isoformat(),
        "judge_model":     JUDGE_MODEL,
        "source_files":    [str(f) for f in source_files],
        "total_requests":  len(all_records) - skipped,
        "output_path":     str(out_path),
    }
    with open(batch_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Metadata : {batch_dir / 'meta.json'}")
    print(f"\nCheck status:")
    print(f"  python3 compare_results_with_ground_truth/judge.py --batch-status {batch_job.name}")


# ---------------------------------------------------------------------------
# Batch mode — status
# ---------------------------------------------------------------------------

def run_batch_status(job_name: str) -> None:
    batch_job = client.batches.get(name=job_name)
    state     = batch_job.state.name
    print(f"Job  : {batch_job.name}")
    print(f"State: {state}")
    if state == "JOB_STATE_SUCCEEDED":
        print(f"\nReady to collect:")
        print(f"  python3 compare_results_with_ground_truth/judge.py --batch-collect {job_name}")


# ---------------------------------------------------------------------------
# Batch mode — collect
# ---------------------------------------------------------------------------

def run_batch_collect(job_name: str) -> None:
    batch_job = client.batches.get(name=job_name)
    state     = batch_job.state.name

    if state != "JOB_STATE_SUCCEEDED":
        sys.exit(f"Batch not complete yet (state: {state}).")

    folder    = job_folder_name(job_name)
    batch_dir = JUDGE_BATCHES / folder
    meta_path = batch_dir / "meta.json"

    if not meta_path.exists():
        sys.exit(f"meta.json not found at {meta_path}. Was this batch submitted with judge.py?")

    with open(meta_path) as f:
        batch_meta = json.load(f)

    out_path = Path(batch_meta["output_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Re-load source records so we can reconstruct full output records.
    source_records: dict[str, dict] = {}
    for source_file in batch_meta["source_files"]:
        for rec in load_results_file(Path(source_file)):
            key = make_key(rec["run_id"], rec["flaw_category"], rec["chart_name"], rec.get("repetition", 1))
            source_records[key] = rec

    print(f"Downloading results for {job_name}...")
    raw_bytes = client.files.download(file=batch_job.dest.file_name)
    raw_text  = raw_bytes.decode("utf-8")

    saved = errors = 0

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        entry = json.loads(line)
        key   = entry.get("key", "")

        try:
            source_run_id, flaw_category, chart_name, repetition = parse_key(key)
        except (ValueError, IndexError):
            print(f"[WARN] Could not parse key: {key!r}")
            continue

        if "status" in entry and not entry.get("response"):
            print(f"[ERR]  {flaw_category}/{chart_name} rep {repetition} — {entry['status']}")
            errors += 1
            continue

        resp = entry.get("response", {})
        try:
            text    = resp["candidates"][0]["content"]["parts"][0]["text"]
            verdict = json.loads(text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[ERR]  {flaw_category}/{chart_name} rep {repetition} — could not parse verdict: {e}")
            errors += 1
            continue

        usage = extract_usage_batch(resp.get("usageMetadata", {}))
        src   = source_records.get(key, {})

        try:
            gt = load_metadata(flaw_category, chart_name)
            flaw_type        = gt.get("flaw_type", flaw_category)
            flaw_description = gt.get("description", "")
        except FileNotFoundError:
            flaw_type        = flaw_category
            flaw_description = ""

        record = make_record(
            job_name,
            src.get("model", "unknown"),
            source_run_id,
            flaw_category, chart_name, repetition,
            flaw_type, flaw_description,
            src.get("response_text", ""),
            verdict, usage,
        )

        with open(out_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        saved += 1

    print(f"\nDone. Saved {saved}, errors {errors}.")
    print(f"Output : {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LLM-as-a-judge: score model responses against ground-truth flaw metadata."
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--model",
        metavar="MODEL",
        help="Process all collected batches for this model (e.g. kimi, gemini_flash).",
    )
    source.add_argument(
        "--results",
        metavar="FILE",
        help="Path to a specific results.jsonl file to judge.",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--batch",
        action="store_true",
        help="Submit judge calls as a Gemini batch job (async, cheaper).",
    )
    mode.add_argument(
        "--batch-status",
        metavar="JOB_NAME",
        help="Check status of a submitted judge batch.",
    )
    mode.add_argument(
        "--batch-collect",
        metavar="JOB_NAME",
        help="Collect results of a completed judge batch.",
    )

    args = parser.parse_args()

    # --batch-status and --batch-collect don't need a source
    if not args.batch_status and not args.batch_collect:
        if not args.model and not args.results:
            parser.error("Specify --model or --results.")

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
