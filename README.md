# Can LLMs Critique Charts? — Evaluation

Evaluation code and results for the dissertation **"Can LLMs Critique Charts? Evaluating Flaw Detection Under Zero-Shot and Taxonomy-Guided Prompting."**

Flawed charts (45 flaw categories, ~600 charts) are sent to three LLMs — GPT-5, Gemini Flash, and Kimi — under two prompting conditions:

- **Zero-shot (free):** the model is simply asked to critique the chart   (`send_to_models/`).
- **Taxonomy-guided:** the model is additionally given the visualization-flaw   taxonomy as part of the prompt (`taxonomy_guided/`).

Each model response is then scored against ground-truth metadata by an LLM-as-judge (`compare_results_with_ground_truth/`), and the judged results are analysed and plotted. The companion **dataset-construction** repository builds the `flawed_charts/` used here.

## Repository structure

The dataset under evaluation:

```
flawed_charts/        # Input dataset: <flaw_category>/{png, code, metadata}
```

### Zero-shot approach

The chart is sent to the model with no taxonomy in the prompt. The model's free-text critique is then mapped onto the flaw taxonomy by an LLM-as-a-judge.

```
send_to_models/                     # Send each chart to a model — evaluate_{gpt5,gemini_flash,kimi}.py
results/                            # Its results: raw model responses (per model: sync/ + batches/)
compare_results_with_ground_truth/  # LLM-as-a-judge — maps free-text responses onto the taxonomy
                                    #   judge.py, evaluation_prompt.md, mapped_results/
```

### Taxonomy-guided approach

The flaw taxonomy is included in the prompt, so the model's response already references taxonomy categories directly.

```
taxonomy_guided/                    # Send each chart to a model with the taxonomy prompt (evaluate_*.py + prompt.md)
taxonomy_guided_results/            # Its results: raw model responses (per model)
```

### Analysis & figures

```
statistical_analysis_zero_shot/     # Statistical / significance tests
figure_generation/                  # Figure scripts (plot_*.py)
└── figures/                        #   generated figures (PDF + PNG) are written here
```

### Other

```
requirements.txt
.env                                # API keys (not committed — see .env.example)
```

Within `results/` and `taxonomy_guided_results/`, each model folder holds a `sync/<timestamp>.jsonl` for synchronous runs and `batches/<batch_id>/` folders (each with `meta.json` after submit and `results.jsonl` after collect).

To regenerate the figures, run the scripts from inside `figure_generation/` (they read the results at the repo root and write into `figure_generation/figures/`):

```bash
cd figure_generation
python plot_detection_by_taxonomy.py
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```
GPT_API_KEY=...
GEMINI_API_KEY=...
GEMINI_API_KEY_NAME=...
GEMINI_API_PROJECT=...
KIMI_API_KEY=...
```

---

## Running `evaluate_gpt5.py`

All commands are run from the project root (`dataset_evaluation/`).

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

Submits all requests at once to the OpenAI Batch API. **50% cheaper** than synchronous, higher rate  limits, results within 24 hours. Recommended for full dataset runs.

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

All commands are run from the project root (`dataset_evaluation/`).

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

All commands are run from the project root (`dataset_evaluation/`).

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
