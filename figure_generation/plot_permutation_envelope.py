"""
Permutation test for delta detection rates (taxonomy-guided vs free-prompt).

Null hypothesis: there is no real difference between the two conditions;
the labels "taxonomy" and "free" are arbitrary and any observed delta is
just chance.

Procedure (per row = per flaw type, independently):
    with probability 0.5, swap (free, tax) -> (tax, free)
which equivalently flips the sign of that row's delta. Repeat B times,
sort each shuffled delta vector ascending, then compute the 2.5th and
97.5th percentile per rank position to get a 95% null envelope.

Output: figures/permutation_envelope.pdf + .png
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
OUT_PDF        = FIGURES_DIR / "permutation_envelope.pdf"
OUT_PNG        = FIGURES_DIR / "permutation_envelope.png"

GREEN = "#2ca02c"
RED   = "#d62728"
BLUE  = "#1f77b4"
GRAY  = "#888888"

# Small B for a quick sanity-check run. For publication-quality p-values
# bump this to 10_000 or 50_000.
B    = 1000000
SEED = 42


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
    rates["delta"] = rates["tax"] - rates["free"]
    rates_sorted = rates.sort_values("delta")  # ascending

    N = len(rates_sorted)
    print(f"N flaw types: {N}")
    print(f"B permutations: {B}")

    # Detection-rate matrix, shape (N, 2): columns = [free, tax]
    M = rates[["free", "tax"]].to_numpy(dtype=float)
    deltas_unsorted = M[:, 1] - M[:, 0]               # tax - free

    # Observed: sort ascending (matches the original bar chart's order)
    observed_sorted = np.sort(deltas_unsorted)

    # Permutation test.
    # For each row independently, with prob 0.5 swap the two columns.
    # Swapping is equivalent to flipping the sign of that row's delta.
    rng = np.random.default_rng(SEED)
    sim_sorted = np.empty((B, N), dtype=float)
    for b in range(B):
        swap  = rng.random(N) < 0.5
        signs = np.where(swap, -1.0, 1.0)
        sim_sorted[b] = np.sort(deltas_unsorted * signs)

    lo  = np.percentile(sim_sorted, 2.5, axis=0)
    hi  = np.percentile(sim_sorted, 97.5, axis=0)
    med = np.percentile(sim_sorted, 50,   axis=0)

    # Global two-sided p-value.
    # Under sign-flip permutation, |Δ_i| is invariant — so max|Δ|, var(Δ),
    # Σ|Δ| are all useless as test statistics. What does change is anything
    # sensitive to the sign pattern. We use the signed mean:
    #     T = mean(Δ_i)
    # which asks "do taxonomy-guided rates lean systematically higher (or
    # lower) than free-prompt rates, averaged across flaw types?"
    obs_mean = float(np.mean(deltas_unsorted))
    sim_mean = sim_sorted.mean(axis=1)
    p_global = (np.sum(np.abs(sim_mean) >= abs(obs_mean)) + 1) / (B + 1)

    # Per-rank "outside envelope?" flag
    outside = (observed_sorted < lo) | (observed_sorted > hi)
    n_outside = int(outside.sum())

    print(f"Observed mean Δ: {obs_mean:+.2f} pp")
    print(f"Global two-sided p (signed mean): {p_global:.4f}")
    print(f"Rank positions outside 95% envelope: {n_outside} / {N}  "
          f"(chance expectation ≈ {0.05 * N:.1f})")

    # ---- Plot ----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))

    ranks = np.arange(1, N + 1)

    ax.fill_between(
        ranks, lo, hi,
        color=GRAY, alpha=0.25,
        label="95% null envelope (per-rank 2.5–97.5%)",
    )
    ax.plot(
        ranks, med,
        color=GRAY, linewidth=1.0, linestyle="--",
        label="Null median",
    )
    ax.plot(
        ranks, observed_sorted,
        color=BLUE, linewidth=1.6,
        label="Observed sorted Δ",
    )
    # Highlight observed points that fall outside the envelope
    inside_mask = ~outside
    ax.scatter(
        ranks[inside_mask], observed_sorted[inside_mask],
        s=22, color=BLUE, zorder=3,
    )
    ax.scatter(
        ranks[outside], observed_sorted[outside],
        s=34, color=RED, zorder=4,
        label="Observed outside envelope",
    )

    ax.axhline(0, color="black", linewidth=0.6, alpha=0.6)
    ax.set_xlabel("Rank position (1 = most negative Δ)", fontsize=11)
    ax.set_ylabel("Δ detection rate (pp): taxonomy − free-prompt", fontsize=11)
    ax.set_title(
        f"Permutation envelope (B = {B}, seed = {SEED}) "
        f"— signed-mean p = {p_global:.3f}, "
        f"{n_outside}/{N} outside band",
        fontsize=12,
    )
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, color="#bbb", alpha=0.6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.set_axisbelow(True)
    ax.set_xlim(0.5, N + 0.5)

    plt.tight_layout(pad=0.5)
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUT_PNG, bbox_inches="tight", pad_inches=0.05, dpi=200)
    print(f"Saved: {OUT_PDF}")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
