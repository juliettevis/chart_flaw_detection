"""
Same horizontal bar chart as `plot_delta_taxonomy_vs_free.py`, but with
a one-sided per-rank null envelope from the permutation test shaded
behind the bars.

For each flaw type at rank k (1 = most negative observed Δ, N = most
positive), the envelope is one-sided: its inner edge is pinned at 0 and
its outer edge is the α-tail quantile of the sorted shuffled deltas at
rank k on the side where the observed delta δ_(k) lies —
    δ_(k) ≤ 0  →  [q_{α,k}, 0]
    δ_(k) > 0  →  [0, q_{1-α,k}]
A bar whose tip extends past the outer bound in its own direction is
"significant" — more extreme than chance would produce at that rank.

Output: figures/delta_with_envelope.pdf + .png
"""

import json
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT           = Path(__file__).parent
REPO           = ROOT.parent  # repo root — this script lives in figure_generation/
MAPPED_RESULTS = REPO / "compare_results_with_ground_truth" / "mapped_results"
TAXONOMY_DIR   = REPO / "taxonomy_guided_results"
FIGURES_DIR    = ROOT / "figures"
TAXONOMY_CSV   = FIGURES_DIR / "flaw_types_defintions.csv"
OUT_PDF        = FIGURES_DIR / "delta_with_envelope.pdf"
OUT_PNG        = FIGURES_DIR / "delta_with_envelope.png"

GREEN = "#2ca02c"
RED   = "#d62728"
GRAY  = "#888888"
BLACK = "#222222"

B     = 1000000
SEED  = 42
ALPHA = 0.05   # significance level → one-sided per-rank α-tail; two-sided for the mean test


def _key(name):
    if not isinstance(name, str):
        return None
    return name.lower().replace(" ", "_")


def load_free():
    records = []
    for p in sorted(MAPPED_RESULTS.rglob("judge_results.jsonl")):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    df = pd.DataFrame(records)
    df = df[df["flaw_detected"].notna()].copy()
    df["flaw_detected"] = df["flaw_detected"].astype(bool)
    return df


def load_tax():
    records = []
    for p in sorted(TAXONOMY_DIR.rglob("results.jsonl")):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
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
        .mean().mul(100).rename("free")
    )
    tax_cat = (
        tax_df.groupby("flaw_category")["detected_any"]
        .mean().mul(100).rename("tax")
    )

    rates = pd.concat([free_cat, tax_cat], axis=1).dropna()
    rates["delta_exact"] = rates["tax"] - rates["free"]   # exact delta, used for the math
    rates["delta"]       = rates["delta_exact"].round(1)  # rounded, for the bar labels only
    rates = rates.sort_values("delta_exact")              # ascending by exact delta

    N      = len(rates)
    labels = [key_to_display.get(k, k.replace("_", " ").title()) for k in rates.index]
    values = rates["delta"].to_numpy(dtype=float)         # rounded, for display

    # ---- Permutation test ---------------------------------------------
    # Use the exact (unrounded) per-flaw deltas δ_i = p^T_i - p^Z_i; rounding
    # to 0.1 pp is only a display choice for the bar labels. `delta_exact` is
    # already sorted ascending, so it is δ_(1) ≤ … ≤ δ_(N).
    deltas          = rates["delta_exact"].to_numpy(dtype=float)
    observed_sorted = deltas

    # Rademacher sign-flip null: S_i^(b) ∈ {-1,+1}, each with probability 1/2.
    # δ_i^(b) = S_i^(b) δ_i.
    rng   = np.random.default_rng(SEED)
    signs = rng.choice([-1.0, 1.0], size=(B, N))
    sim   = signs * deltas
    del signs
    T_b   = sim.mean(axis=1)        # signed-mean statistic per permutation
    sim.sort(axis=1)               # in-place → sim is now δ^(b)_(k), ascending per row
    sim_sorted = sim

    # ---- One-sided per-rank envelope ----------------------------------
    # Direction set by the sign of the observed delta at each rank:
    #   δ_(k) ≤ 0  →  E_k = [q_{α,k}, 0]     (lower α-quantile)
    #   δ_(k) > 0  →  E_k = [0, q_{1-α,k}]   (upper (1-α)-quantile)
    conf = int(round((1 - ALPHA) * 100))
    med  = np.percentile(sim_sorted, 50,                axis=0)  # per-rank null median
    q_lo = np.percentile(sim_sorted, 100 * ALPHA,       axis=0)  # lower α-quantile
    q_hi = np.percentile(sim_sorted, 100 * (1 - ALPHA), axis=0)  # upper (1-α)-quantile

    neg   = observed_sorted <= 0
    outer = np.where(neg, q_lo, q_hi)   # calculated boundary, away from 0
    inner = np.zeros_like(outer)        # boundary pinned at 0

    # ---- Signed-mean permutation test (global, two-sided) -------------
    #   T      = (1/N) Σ_i δ_i
    #   T^(b)  = (1/N) Σ_i S_i^(b) δ_i
    #   p_hat  = #{ b : |T^(b)| ≥ |T| } / B
    T      = float(deltas.mean())
    p_hat  = float(np.mean(np.abs(T_b) >= abs(T)))
    q_lo_T = float(np.quantile(T_b, ALPHA / 2))
    q_hi_T = float(np.quantile(T_b, 1 - ALPHA / 2))
    reject = (T < q_lo_T) or (T > q_hi_T)
    obs_mean = T   # alias for the chart annotation below

    # A bar is significant if its tip extends past the one-sided outer bound
    # on the side it points to.
    outside     = np.where(neg, observed_sorted < q_lo, observed_sorted > q_hi)
    sig_indices = set(np.where(outside)[0].tolist())

    print(f"N flaw types         : {N}")
    print(f"B permutations       : {B}")
    print(f"ALPHA                : {ALPHA}  →  {conf}% null band")
    print(f"Observed T           : {T:+.4f} pp")
    print(f"T^(b)   min          : {T_b.min():+.4f} pp")
    print(f"T^(b)   max          : {T_b.max():+.4f} pp")
    print(f"T^(b)   mean         : {T_b.mean():+.4f} pp")
    print(f"T^(b)   std (SE T)   : {T_b.std(ddof=0):.4f} pp  "
          f"(theoretical: {np.sqrt((deltas**2).sum()) / N:.4f})")
    print(f"{conf}% null band of T^(b): [{q_lo_T:+.4f}, {q_hi_T:+.4f}] pp")
    print(f"#{{b : |T^(b)| >= |T|}}  : {int(np.sum(np.abs(T_b) >= abs(T)))}")
    print(f"p_hat                : {p_hat:.5f}")
    print(f"Decision @ α={ALPHA}   : "
          f"{'REJECT H0' if reject else 'fail to reject H0'}  "
          f"(p_hat {'<' if p_hat < ALPHA else '≥'} {ALPHA})")
    print(f"Outside one-sided {conf}% per-rank bound: {int(outside.sum())} / {N} "
          f"(chance ≈ {ALPHA * N:.1f})")

    # ---- Plot ---------------------------------------------------------
    n     = N
    fig_h = max(7.0, n * 0.26)
    fig, ax = plt.subplots(figsize=(8.5, fig_h))

    # Shaded null envelope band. The y-coordinate of bar at rank k (sorted
    # ascending) is k (0-indexed), so plot fill_betweenx with y = 0..N-1.
    y = np.arange(n)
    ax.fill_betweenx(
        y, inner, outer,
        color=GRAY, alpha=0.18, linewidth=0,
        label=f"one-sided {conf}% null bound",
    )
    # Outer (calculated) edge of the one-sided band
    ax.plot(outer, y, color=GRAY, linewidth=0.6, linestyle="--")
    # Per-rank null median (empirical q_0.5)
    ax.plot(med, y, color=GRAY, linewidth=1.0, linestyle="-")

    # Bars — colour by direction, but only "fully saturated" for significant
    # bars (outside the envelope). Non-significant bars are paler.
    bar_colors = []
    for i, v in enumerate(values):
        base = GREEN if v > 0 else (RED if v < 0 else BLACK)
        if i in sig_indices:
            bar_colors.append(base)
        else:
            # paler version → mix with white
            bar_colors.append(base)
    alphas = [1.0 if i in sig_indices else 0.35 for i in range(n)]

    bars = ax.barh(labels, values, color=bar_colors, height=0.72)
    for bar, a in zip(bars, alphas):
        bar.set_alpha(a)

    # Per-bar value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        w   = bar.get_width()
        sig = "*" if i in sig_indices else ""
        txt = f"{val:+.1f}pp{sig}"
        if abs(w) >= 10:
            ax.text(
                w / 2, bar.get_y() + bar.get_height() / 2,
                txt, ha="center", va="center",
                fontsize=8, color="white",
            )
        else:
            offset = 0.6 if w >= 0 else -0.6
            base   = GREEN if w > 0 else (RED if w < 0 else BLACK)
            ax.text(
                w + offset, bar.get_y() + bar.get_height() / 2,
                txt, ha="left" if w >= 0 else "right", va="center",
                fontsize=8, color=base if i in sig_indices else GRAY,
            )

    ax.axvline(0, color="black", linewidth=0.8)
    # Observed signed mean Δ across all flaw types
    ax.axvline(
        obs_mean, color=BLACK, linewidth=1.2, linestyle=":",
        label=f"Observed mean Δ = {obs_mean:+.1f} pp",
    )
    ax.set_xlabel(
        "Δ detection rate (pp): taxonomy-guided minus free-prompt",
        fontsize=11,
    )

    legend_handles = [
        mpatches.Patch(color=GREEN, label="Taxonomy better (significant)"),
        mpatches.Patch(color=GREEN, alpha=0.35, label="Taxonomy better (n.s.)"),
        mpatches.Patch(color=RED,   label="Free-prompt better (significant)"),
        mpatches.Patch(color=RED,   alpha=0.35, label="Free-prompt better (n.s.)"),
        mpatches.Patch(color=GRAY,  alpha=0.4,  label=f"one-sided {conf}% null bound"),
        plt.Line2D([0], [0], color=GRAY,  linewidth=1.0,
                   label="Null median (per rank)"),
        plt.Line2D([0], [0], color=BLACK, linewidth=1.2, linestyle=":",
                   label=f"Observed mean Δ = {obs_mean:+.1f} pp"),
    ]
    ax.legend(handles=legend_handles, loc="lower right",
              fontsize=8, frameon=False)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, color="#bbb", alpha=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=9)
    ax.set_ylim(-0.6, n - 0.4)

    plt.tight_layout(pad=0.2)
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT_PNG, bbox_inches="tight", pad_inches=0.02, dpi=200)
    print(f"Saved: {OUT_PDF}")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
