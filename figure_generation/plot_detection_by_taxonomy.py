"""
Detection rate per flaw type, grouped by Stage and Category.

Produces a horizontal stacked-bar chart with three label columns
(Stage, Category, Flaw Type) on the left and one bar column per model
on the right. Output: PDF (for LaTeX) + PNG (for preview).

Usage:
    python plot_detection_by_taxonomy.py
"""

import json
from itertools import groupby
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT          = Path(__file__).parent
REPO          = ROOT.parent  # repo root — this script lives in figure_generation/
JUDGE_RESULTS = REPO / "compare_results_with_ground_truth" / "mapped_results"
FIGURES_DIR   = ROOT / "figures"
TAXONOMY_CSV  = FIGURES_DIR / "flaw_types_defintions.csv"
OUT_PDF       = FIGURES_DIR / "detection_by_taxonomy.pdf"
OUT_PNG       = FIGURES_DIR / "detection_by_taxonomy.png"

MODELS = ["gemini_flash", "gpt5", "kimi"]
MODEL_DISPLAY = {
    "gemini_flash": "Gemini 3 Flash",
    "gpt5":         "GPT-5.4",
    "kimi":         "Kimi K2.6",
}
STAGE_DISPLAY = {"Visualization Design": "Visualization\nDesign"}

TRUE_COLOR  = "#2d6a4f"
FALSE_COLOR = "#e63946"


def load_records(model: str) -> pd.DataFrame:
    records = []
    for p in sorted((JUDGE_RESULTS / model).rglob("judge_results.jsonl")):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    df = pd.DataFrame(records)
    if not df.empty:
        df["model"] = model
    return df


def main():
    # ---------- data ----------
    taxonomy = pd.read_csv(TAXONOMY_CSV, sep=";")
    taxonomy["flaw_key"] = taxonomy["Flaw Type"].str.lower().str.replace(" ", "_")
    taxonomy = taxonomy[taxonomy["flaw_key"] != "cluttering"].reset_index(drop=True)

    per_model = {m: load_records(m) for m in MODELS}
    all_df = pd.concat(
        [d for d in per_model.values() if not d.empty],
        ignore_index=True,
    )

    # Attach Stage / Category to each row using the taxonomy
    key_to_stage = dict(zip(taxonomy["flaw_key"], taxonomy["Stage"]))
    key_to_cat   = dict(zip(taxonomy["flaw_key"], taxonomy["Category"]))
    all_df["Stage"]    = all_df["flaw_category"].map(key_to_stage)
    all_df["Category"] = all_df["flaw_category"].map(key_to_cat)

    # Per-model detection rate per flaw category
    rates = {}
    for m in MODELS:
        d = per_model[m]
        rates[m] = (d.groupby("flaw_category")["flaw_detected"].mean()
                    if not d.empty else pd.Series(dtype=float))

    # Pooled rates across all three models, per Stage and per (Stage, Category)
    stage_rate = all_df.groupby("Stage")["flaw_detected"].mean()
    cat_rate   = all_df.groupby(["Stage", "Category"])["flaw_detected"].mean()
    flaw_rate  = all_df.groupby("flaw_category")["flaw_detected"].mean()

    for m in MODELS:
        missing = [k for k in taxonomy["flaw_key"] if k not in rates[m].index]
        if missing:
            print(f"[{m}] no data for {len(missing)} flaw types: {missing}")

    n_flaws  = len(taxonomy)
    n_models = len(MODELS)

    # ---------- layout ----------
    # Outer split: label area | bars area. Bars use a nested gridspec so we
    # can keep them close together (small inter-bar wspace) while still
    # leaving breathing room between the labels and the first bar.
    # Explicit margins remove the right-side whitespace.
    fig_h = max(11.0, n_flaws * 0.28)
    fig = plt.figure(figsize=(9, fig_h))
    outer = fig.add_gridspec(
        1, 2, width_ratios=[2.8, 2.2], wspace=0.05,
        left=0.04, right=0.995, top=0.955, bottom=0.025,
    )
    gs_bars = outer[1].subgridspec(1, n_models, wspace=0.06)

    ax_lbl  = fig.add_subplot(outer[0])
    ax_bars = [fig.add_subplot(gs_bars[i], sharey=ax_lbl) for i in range(n_models)]

    y_pos = [n_flaws - 1 - i for i in range(n_flaws)]

    # ---------- bars ----------
    for ax, model in zip(ax_bars, MODELS):
        true_pcts  = [rates[model].get(k, 0.0) * 100 for k in taxonomy["flaw_key"]]
        false_pcts = [100 - p for p in true_pcts]
        ax.barh(y_pos, true_pcts,  color=TRUE_COLOR,  height=0.78,
                label="True (detected)")
        ax.barh(y_pos, false_pcts, left=true_pcts, color=FALSE_COLOR, height=0.78,
                label="False (not detected)")
        for y, pct in zip(y_pos, true_pcts):
            label_txt = f"{pct:.0f}%"
            if pct >= 18:
                ax.text(pct / 2, y, label_txt,
                        ha="center", va="center", fontsize=6.5,
                        color="white", fontweight="bold")
            elif pct > 0:
                ax.text(pct + 1.5, y, label_txt,
                        ha="left", va="center", fontsize=6.5,
                        color=TRUE_COLOR, fontweight="bold")
        ax.set_title(MODEL_DISPLAY[model], fontsize=12, fontweight="bold", pad=6)
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 50, 100])
        xtick_labels = ax.set_xticklabels(["0%", "50%", "100%"], fontsize=8.5)
        xtick_labels[0].set_horizontalalignment("left")
        xtick_labels[-1].set_horizontalalignment("right")
        ax.tick_params(axis="y", which="both", left=False, labelleft=False)
        ax.grid(axis="x", linestyle=":", linewidth=0.5, color="#bbb", alpha=0.6)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    # ---------- label axis ----------
    ax_lbl.set_xlim(0, 1)
    ax_lbl.set_ylim(-0.7, n_flaws - 0.3)
    ax_lbl.set_xticks([])
    ax_lbl.set_yticks([])
    for spine in ("top", "right", "bottom", "left"):
        ax_lbl.spines[spine].set_visible(False)

    X_STAGE   = 0
    X_CAT     = 0.28
    X_PCT_OFF = 0.3   # inline % offset from X_CAT for 1-row categories
    X_FLAW    = 0.93   # right-aligned flaw type label
    X_AVG     = 1   # average detection rate, right-aligned just before bars

    # Spans for grouped labels
    stage_spans = []
    for stage, group in groupby(enumerate(taxonomy["Stage"]), key=lambda t: t[1]):
        items = list(group)
        stage_spans.append((stage, items[0][0], items[-1][0]))

    cat_spans = []
    for key, group in groupby(
        enumerate(zip(taxonomy["Stage"], taxonomy["Category"])),
        key=lambda t: t[1],
    ):
        items = list(group)
        cat_spans.append((key, items[0][0], items[-1][0]))

    # Stage labels: bold name above, pooled-detection % below.
    # Multi-line names need extra room so the % doesn't collide with them.
    for stage, start, end in stage_spans:
        cy = n_flaws - 1 - (start + end) / 2
        pct = stage_rate.get(stage, 0.0) * 100
        label = STAGE_DISPLAY.get(stage, stage)
        multiline = "\n" in label
        label_off = 0.34 if multiline else 0.25
        pct_off   = -0.60 if multiline else -0.32
        ax_lbl.text(X_STAGE, cy + label_off, label,
                    ha="left", va="center", fontsize=11, fontweight="bold")
        ax_lbl.text(X_STAGE, cy + pct_off, f"{pct:.0f}%",
                    ha="left", va="center", fontsize=8.5, color="#555")

    # Category labels: italic name; multi-row groups stack name above the %,
    # 1-row groups place the % inline next to the name (keeping the same
    # italic / gray styling).
    for (stage, cat), start, end in cat_spans:
        cy = n_flaws - 1 - (start + end) / 2
        pct = cat_rate.get((stage, cat), 0.0) * 100
        if start == end:
            ax_lbl.text(X_CAT, cy, cat,
                        ha="left", va="center", fontsize=10, fontstyle="italic")
            ax_lbl.text(X_CAT + X_PCT_OFF, cy, f"{pct:.0f}%",
                        ha="left", va="center", fontsize=8.5, color="#555")
        else:
            ax_lbl.text(X_CAT, cy + 0.22, cat,
                        ha="left", va="center", fontsize=10, fontstyle="italic")
            ax_lbl.text(X_CAT, cy - 0.30, f"{pct:.0f}%",
                        ha="left", va="center", fontsize=8.5, color="#555")

    # Flaw type per row: right-aligned, then average detection rate at far right
    for i, row in taxonomy.iterrows():
        y = n_flaws - 1 - i
        ax_lbl.text(X_FLAW, y, row["Flaw Type"],
                    ha="right", va="center", fontsize=9)
        avg = flaw_rate.get(row["flaw_key"], 0.0) * 100
        ax_lbl.text(X_AVG, y, f"{avg:.0f}%",
                    ha="right", va="center", fontsize=8, color="#555")

    # ---------- group separators ----------
    # Stage dividers: solid black, ONLY in the first column (stage column).
    for stage, start, end in stage_spans[:-1]:
        sep_y = n_flaws - 1 - end - 0.5
        ax_lbl.axhline(sep_y, color="black", linewidth=0.6,
                       xmin=0.0, xmax=X_CAT)

    # Category dividers: light gray, ONLY from the second column onward
    # in the label axis, and full width on the bar axes.
    # Drawn at every category boundary (including stage boundaries — the
    # stage divider sits next to it in column 1).
    for _, start, end in cat_spans[:-1]:
        sep_y = n_flaws - 1 - end - 0.5
        ax_lbl.axhline(sep_y, color="black", linewidth=0.6,
                       xmin=X_CAT, xmax=1.0)
        for ax in ax_bars:
            ax.axhline(sep_y, color="#bbb", linewidth=0.5)

    # ---------- legend (top-right, tight against the chart) ----------
    handles, labels = ax_bars[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right",
               bbox_to_anchor=(0.995, 0.998), ncol=2, frameon=False, fontsize=10)

    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUT_PNG, bbox_inches="tight", pad_inches=0.05, dpi=200)
    print(f"Saved: {OUT_PDF}")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
