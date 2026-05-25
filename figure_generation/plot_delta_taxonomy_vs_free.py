"""
Horizontal bar chart: taxonomy-guided vs free-prompt delta in overall detection
rate per flaw type (averaged across all three models).

Green bars = taxonomy better, red bars = free-prompt better.
Flaw types sorted by delta value (ascending → most negative at bottom).

Output: figures/delta_taxonomy_vs_free.pdf + .png
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT           = Path(__file__).parent
REPO           = ROOT.parent  # repo root — this script lives in figure_generation/
MAPPED_RESULTS = REPO / "compare_results_with_ground_truth" / "mapped_results"
TAXONOMY_DIR   = REPO / "taxonomy_guided_results"
FIGURES_DIR    = ROOT / "figures"
TAXONOMY_CSV   = FIGURES_DIR / "flaw_types_defintions.csv"
OUT_PDF        = FIGURES_DIR / "delta_taxonomy_vs_free.pdf"
OUT_PNG        = FIGURES_DIR / "delta_taxonomy_vs_free.png"

GREEN = "#2ca02c"
RED   = "#d62728"
GRAY  = "#888888"

# Permutation test settings
B     = 1000000
SEED  = 42
ALPHA = 0.05   # significance level → (1-ALPHA) two-sided confidence band


def _key(name: object) -> str | None:
    if not isinstance(name, str):
        return None
    return name.lower().replace(" ", "_")


def load_free() -> pd.DataFrame:
    records = []
    for p in sorted(MAPPED_RESULTS.rglob("judge_results.jsonl")):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df = df[df["flaw_detected"].notna()].copy()
    df["flaw_detected"] = df["flaw_detected"].astype(bool)
    return df


def load_tax() -> pd.DataFrame:
    records = []
    for p in sorted(TAXONOMY_DIR.rglob("results.jsonl")):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["other_flaws_mentioned"] = df["other_flaws_mentioned"].apply(
        lambda x: x if isinstance(x, list) else []
    )
    df["primary_key"]      = df["primary_flaw_type"].apply(_key)
    df["detected_primary"] = df["primary_key"] == df["flaw_category"]
    df["other_keys"]       = df["other_flaws_mentioned"].apply(
        lambda lst: [k for k in (_key(f) for f in lst) if k]
    )
    df["detected_any"] = df.apply(
        lambda r: bool(r["detected_primary"]) or r["flaw_category"] in r["other_keys"],
        axis=1,
    )
    return df


def main():
    taxonomy = pd.read_csv(TAXONOMY_CSV, sep=";")
    taxonomy["flaw_key"] = taxonomy["Flaw Type"].str.lower().str.replace(" ", "_")
    key_to_display = dict(zip(taxonomy["flaw_key"], taxonomy["Flaw Type"]))

    free_df = load_free()
    tax_df  = load_tax()

    free_cat = (
        free_df.groupby("flaw_category")["flaw_detected"]
        .mean().mul(100)
        .rename("free")
    )
    tax_cat = (
        tax_df.groupby("flaw_category")["detected_any"]
        .mean().mul(100)
        .rename("tax")
    )

    delta = pd.concat([free_cat, tax_cat], axis=1).dropna()
    delta["delta"] = (delta["tax"] - delta["free"]).round(1)
    delta = delta.sort_values("delta")

    # ---- Permutation test: signed-mean significance --------------------
    # H0: each delta_i is equally likely to be +|delta_i| or -|delta_i|
    # (i.e. the columns "free" and "tax" are exchangeable per row).
    # Sign-flip with Rademacher S_i^(b) in {-1,+1} and compute
    #   T      = (1/N) sum_i delta_i
    #   T^(b)  = (1/N) sum_i S_i^(b) delta_i
    #   p_hat  = #{ b : |T^(b)| >= |T| } / B
    deltas_arr = delta["delta"].to_numpy(dtype=float)
    N = len(deltas_arr)
    T = float(np.mean(deltas_arr))

    rng    = np.random.default_rng(SEED)
    signs  = rng.choice([-1.0, 1.0], size=(B, N))
    T_b    = (signs * deltas_arr).mean(axis=1)
    p_hat  = float(np.mean(np.abs(T_b) >= abs(T)))

    # (1 - ALPHA) two-sided critical values of T^(b) under H0.
    # Reject H0 at level ALPHA iff T < q_lo or T > q_hi  (equivalently iff p_hat < ALPHA).
    q_lo   = float(np.quantile(T_b, ALPHA / 2))
    q_hi   = float(np.quantile(T_b, 1 - ALPHA / 2))
    reject = (T < q_lo) or (T > q_hi)
    conf   = int(round((1 - ALPHA) * 100))

    print(f"N flaw types        : {N}")
    print(f"B permutations      : {B}")
    print(f"ALPHA               : {ALPHA}  →  {conf}% null band")
    print(f"Observed T          : {T:+.4f} pp")
    print(f"T^(b)   min         : {T_b.min():+.4f} pp")
    print(f"T^(b)   max         : {T_b.max():+.4f} pp")
    print(f"T^(b)   mean        : {T_b.mean():+.4f} pp")
    print(f"T^(b)   std (SE T)  : {T_b.std(ddof=0):.4f} pp  "
          f"(theoretical: {np.sqrt((deltas_arr**2).sum()) / N:.4f})")
    print(f"{conf}% null band of T^(b): [{q_lo:+.4f}, {q_hi:+.4f}] pp")
    print(f"#{{b : |T^(b)| >= |T|}} : {int(np.sum(np.abs(T_b) >= abs(T)))}")
    print(f"p_hat                : {p_hat:.5f}")
    print(f"Decision @ α={ALPHA}  : "
          f"{'REJECT H0' if reject else 'fail to reject H0'}  "
          f"(p_hat {'<' if p_hat < ALPHA else '≥'} {ALPHA})")

    labels = [key_to_display.get(k, k.replace("_", " ").title()) for k in delta.index]
    values = delta["delta"].tolist()
    colors = [GREEN if v > 0 else (RED if v < 0 else GRAY) for v in values]

    n      = len(delta)
    fig_h  = max(7.0, n * 0.26)
    fig, ax = plt.subplots(figsize=(7.5, fig_h))

    bars = ax.barh(labels, values, color=colors, height=0.72)

    for bar, val in zip(bars, values):
        w = bar.get_width()
        txt = f"{val:+.1f}pp"
        if abs(w) >= 8:
            ax.text(
                w / 2, bar.get_y() + bar.get_height() / 2,
                txt, ha="center", va="center",
                fontsize=9, color="white",
            )
        else:
            offset = 0.6 if w >= 0 else -0.6
            ax.text(
                w + offset, bar.get_y() + bar.get_height() / 2,
                txt, ha="left" if w >= 0 else "right", va="center",
                fontsize=9, color=GREEN if w > 0 else RED,
            )

    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Δ detection rate (pp): taxonomy-guided minus free-prompt", fontsize=11)

    import matplotlib.patches as mpatches
    legend_handles = [
        mpatches.Patch(color=GREEN, label="Taxonomy better"),
        mpatches.Patch(color=RED,   label="Free-prompt better"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=10, frameon=False)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, color="#bbb", alpha=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=10)

    # Remove padding above the top bar
    ax.set_ylim(-0.6, n - 0.4)

    plt.tight_layout(pad=0.2)
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT_PNG, bbox_inches="tight", pad_inches=0.02, dpi=200)
    print(f"Saved: {OUT_PDF}")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
