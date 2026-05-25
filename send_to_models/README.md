# `send_to_models/` — model evaluation scripts

Command-line reference for the zero-shot evaluation scripts. Each script sends
the flawed charts to one model and writes the raw responses to `results/<model>/`.

All commands are run from the **repository root**. The three scripts share the
same CLI (`--flawtype`, `--chartname`, `--runs`, `--resume`, `--batch`,
`--batch-status`, `--batch-collect`). The `taxonomy_guided/evaluate_*.py`
scripts mirror this interface but prepend the taxonomy prompt and write to
`taxonomy_guided_results/`.

---

## Running `evaluate_gpt5.py`

### Synchronous mode

Sends one request at a time and saves results immediately. Use this for quick tests or small subsets.

```bash
# All 608 charts
python3 send_to_models/evaluate_gpt5.py

# One flaw category only
python3 send_to_models/evaluate_gpt5.py --flawtype indistinguishable_colors

# One specific chart
python3 send_to_models/evaluate_gpt5.py --flawtype indistinguishable_colors --chartname line_chart_2

# Send each chart 3 times
python3 send_to_models/evaluate_gpt5.py --runs 3

# Resume an interrupted run (skips charts already in the file)
python3 send_to_models/evaluate_gpt5.py --resume results/gpt5/sync/20260430_143012.jsonl
```

Output: `results/gpt5/sync/<timestamp>.jsonl`

---

### Batch mode

Submits all requests at once to the OpenAI Batch API. **50% cheaper** than synchronous, higher rate limits, results within 24 hours. Recommended for full dataset runs.

**Step 1 — Submit:**
```bash
# All charts
python3 send_to_models/evaluate_gpt5.py --batch

# Scoped to a flaw category
python3 send_to_models/evaluate_gpt5.py --batch --flawtype truncated_axis
```

This saves submission metadata to `results/gpt5/batches/<batch_id>/meta.json`. The batch ID is printed — keep it.

**Step 2 — Check status:**
```bash
python3 send_to_models/evaluate_gpt5.py --batch-status batch_abc123
```

Status will be one of: `validating` → `in_progress` → `finalizing` → `completed`.

**Step 3 — Collect results:**
```bash
python3 send_to_models/evaluate_gpt5.py --batch-collect batch_abc123
```

Output: `results/gpt5/batches/<batch_id>/results.jsonl`

> **Note:** The batch input embeds base64-encoded images and can be large. If it exceeds the 200 MB OpenAI limit, the script will exit and suggest using `--flawtype` to split into smaller batches.

---

## Running `evaluate_gemini_flash.py`

Uses `MEDIA_RESOLUTION_HIGH` (1120 tokens/image) for detailed chart analysis. Thinking is set to `MINIMAL` in sync mode and disabled in batch mode.

### Synchronous mode

```bash
# All 608 charts
python3 send_to_models/evaluate_gemini_flash.py

# One flaw category only
python3 send_to_models/evaluate_gemini_flash.py --flawtype indistinguishable_colors

# One specific chart
python3 send_to_models/evaluate_gemini_flash.py --flawtype indistinguishable_colors --chartname line_chart_2

# Send each chart 3 times
python3 send_to_models/evaluate_gemini_flash.py --runs 3

# Resume an interrupted run
python3 send_to_models/evaluate_gemini_flash.py --resume results/gemini_flash/sync/20260430_143012.jsonl
```

Output: `results/gemini_flash/sync/<timestamp>.jsonl`

---

### Batch mode

The batch input embeds base64-encoded images. Maximum file size is 2 GB (well within range for the full dataset).

**Step 1 — Submit:**
```bash
python3 send_to_models/evaluate_gemini_flash.py --batch
python3 send_to_models/evaluate_gemini_flash.py --batch --flawtype truncated_axis
```

**Step 2 — Check status:**
```bash
python3 send_to_models/evaluate_gemini_flash.py --batch-status batches/123456789
```

Status will be one of: `JOB_STATE_PENDING` → `JOB_STATE_RUNNING` → `JOB_STATE_SUCCEEDED`.

**Step 3 — Collect results:**
```bash
python3 send_to_models/evaluate_gemini_flash.py --batch-collect batches/123456789
```

Output: `results/gemini_flash/batches/batches_123456789/results.jsonl`

---

## Running `evaluate_kimi.py`

Images are uploaded once to the Kimi Files API and cached in `results/kimi/image_ids.json`. Subsequent runs and batch submissions reuse the same file IDs via `ms://<file_id>` references — keeping the batch JSONL small (well under the 100 MB limit). Thinking is disabled.

### Synchronous mode

```bash
# All 608 charts
python3 send_to_models/evaluate_kimi.py

# One flaw category only
python3 send_to_models/evaluate_kimi.py --flawtype indistinguishable_colors

# One specific chart
python3 send_to_models/evaluate_kimi.py --flawtype indistinguishable_colors --chartname line_chart_2

# Send each chart 3 times
python3 send_to_models/evaluate_kimi.py --runs 3

# Resume an interrupted run
python3 send_to_models/evaluate_kimi.py --resume results/kimi/sync/20260430_143012.jsonl
```

Output: `results/kimi/sync/<timestamp>.jsonl`

---

### Batch mode

The batch input uses file ID references (no base64), so the JSONL stays tiny regardless of dataset size.

**Step 1 — Submit:**
```bash
# All charts
python3 send_to_models/evaluate_kimi.py --batch

# Scoped to a flaw category
python3 send_to_models/evaluate_kimi.py --batch --flawtype truncated_axis
```

**Step 2 — Check status:**
```bash
python3 send_to_models/evaluate_kimi.py --batch-status batch_abc123
```

**Step 3 — Collect results:**
```bash
python3 send_to_models/evaluate_kimi.py --batch-collect batch_abc123
```

Output: `results/kimi/batches/<batch_id>/results.jsonl`

---

## Output format

Every result file (sync or batch) is a `.jsonl` where each line is a self-contained JSON record:

```json
{
  "run_id": "20260430_143012",
  "timestamp": "2026-04-30T14:30:12+00:00",
  "model": "gpt-5",
  "flaw_category": "truncated_axis",
  "chart_name": "bar_chart_3",
  "repetition": 1,
  "prompt": "Evaluate this chart.",
  "response_text": "The y-axis starts at 80 instead of 0, which exaggerates...",
  "usage": { ... }
}
```

The `usage` field keys differ per model:
- **GPT-5**: `input_tokens`, `output_tokens`, `total_tokens`
- **Gemini Flash**: `prompt_token_count`, `candidates_token_count`, `total_token_count`
- **Kimi**: `prompt_tokens`, `completion_tokens`, `total_tokens`

Records can be joined with the ground-truth metadata on `(flaw_category, chart_name)`.

---

## Notes

- `--runs N` sends each chart–prompt pair N times. Each repetition is a separate, identical request. The `repetition` field (1-indexed) distinguishes them in the output.
- Batch results come back in arbitrary order; scripts use `custom_id` (or `key` for Gemini) internally to match results to the correct chart.
- Sync results and collected batch results are in the same format and can be used interchangeably downstream.
- A batch folder without a `results.jsonl` means it has not been collected yet.
