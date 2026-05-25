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

## Workflow

1. **Send the charts to the models.**
   - *Zero-shot:* `send_to_models/evaluate_{gpt5,gemini_flash,kimi}.py` → `results/`
   - *Taxonomy-guided:* `taxonomy_guided/evaluate_*.py` → `taxonomy_guided_results/`
2. **Map responses onto the taxonomy** — *zero-shot only.* The free-text critiques are scored by the LLM-as-a-judge in `compare_results_with_ground_truth/` → `mapped_results/`. Taxonomy-guided responses already reference taxonomy categories directly, so they skip this step.
3. **Analyse & plot.** Statistics in `statistical_analysis_zero_shot/`; figures via `figure_generation/`.

Each `evaluate_*.py` script supports synchronous and (cheaper) batch runs, scoping by flaw type or chart, repeated runs, and resuming. See **[`send_to_models/README.md`](send_to_models/README.md)** for the full command-line reference and the result-file format.
