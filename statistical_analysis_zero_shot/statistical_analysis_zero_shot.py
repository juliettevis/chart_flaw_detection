"""
Streamlit app for manually reviewing a stratified random sample of judge results.

Strata: model x flaw_detected (gemini_flash/gpt5/kimi x True/False) = 6 strata.
Allocation: n_h = ceil(N_h / N * TARGET_N) per stratum.
Sampling: np.random.default_rng(SEED) draws n_h indices without replacement per stratum.

Reviews are saved to reviews.jsonl alongside this script.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "compare_results_with_ground_truth" / "mapped_results" / "all_mapped_results.jsonl"
CHARTS_DIR = ROOT / "flawed_charts"
REVIEWS_FILE = Path(__file__).resolve().parent / "reviews.jsonl"

SEED = 42
TARGET_N = 44
MODELS = ["gemini_flash", "gpt5", "kimi"]
DETECTED_LEVELS = [True, False]


# ---------- data loading & sampling ----------

@st.cache_data
def load_records() -> list[dict]:
    records = []
    with DATA_FILE.open() as f:
        for line in f:
            records.append(json.loads(line))
    return records


@st.cache_data
def build_sample(seed: int, target_n: int) -> tuple[list[dict], dict]:
    """Return (sampled_records, allocation_info) using the user's allocation rule."""
    records = load_records()
    n_total = len(records)

    # Group records by stratum (model, flaw_detected)
    strata: dict[tuple[str, bool], list[int]] = {}
    for idx, r in enumerate(records):
        key = (r["model"], bool(r["flaw_detected"]))
        strata.setdefault(key, []).append(idx)

    # Allocate: n_h = ceil(N_h / N * target) when there's any remainder, else N_h/N*target
    allocation = {}
    for key in sorted(strata):
        N_h = len(strata[key])
        raw = N_h / n_total * target_n
        n_h = math.ceil(raw) if raw != int(raw) else int(raw)
        allocation[key] = {"N_h": N_h, "raw": raw, "n_h": n_h}

    # Reproducible sampling: one rng, strata processed in sorted order
    rng = np.random.default_rng(seed)
    sampled = []
    for key in sorted(strata):
        pool = strata[key]
        n_h = allocation[key]["n_h"]
        chosen_positions = rng.choice(len(pool), size=n_h, replace=False)
        for pos in sorted(chosen_positions):
            rec = dict(records[pool[pos]])
            rec["_stratum"] = f"{key[0]}_{'true' if key[1] else 'false'}"
            sampled.append(rec)

    info = {
        "n_total": n_total,
        "target_n": target_n,
        "actual_n": sum(a["n_h"] for a in allocation.values()),
        "seed": seed,
        "allocation": allocation,
    }
    return sampled, info


def sample_id(rec: dict) -> str:
    return f"{rec['model']}|||{rec['flaw_category']}|||{rec['chart_name']}|||{rec['repetition']}"


# ---------- review persistence ----------

def load_reviews() -> dict[str, dict]:
    if not REVIEWS_FILE.exists():
        return {}
    reviews = {}
    with REVIEWS_FILE.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            reviews[r["sample_id"]] = r
    return reviews


def save_reviews(reviews: dict[str, dict]) -> None:
    with REVIEWS_FILE.open("w") as f:
        for sid in sorted(reviews):
            f.write(json.dumps(reviews[sid]) + "\n")


# ---------- UI ----------

st.set_page_config(page_title="Zero-shot review", layout="wide")
st.title("Zero-shot stratified-sample review")

sampled, info = build_sample(SEED, TARGET_N)

if "reviews" not in st.session_state:
    st.session_state.reviews = load_reviews()
if "idx" not in st.session_state:
    st.session_state.idx = 0

# Sidebar: methodology summary + progress
with st.sidebar:
    st.header("Sampling methodology")
    st.markdown(
        f"- **N (population)**: {info['n_total']}\n"
        f"- **Target n**: {info['target_n']}\n"
        f"- **Actual n (after ceil)**: {info['actual_n']}\n"
        f"- **Seed**: {info['seed']} (`np.random.default_rng`)\n"
        f"- **Allocation rule**: $n_h = \\lceil N_h / N \\cdot n \\rceil$ when fractional"
    )

    st.subheader("Strata allocation")
    table_rows = []
    for key in sorted(info["allocation"]):
        a = info["allocation"][key]
        table_rows.append({
            "stratum": f"{key[0]} | {'true' if key[1] else 'false'}",
            "N_h": a["N_h"],
            "raw n_h": f"{a['raw']:.3f}",
            "final n_h": a["n_h"],
        })
    st.dataframe(table_rows, hide_index=True, use_container_width=True)

    n_reviewed = sum(1 for r in sampled if sample_id(r) in st.session_state.reviews)
    st.subheader("Progress")
    st.progress(n_reviewed / len(sampled))
    st.caption(f"{n_reviewed} / {len(sampled)} reviewed")

    if st.button("Reload reviews from disk"):
        st.session_state.reviews = load_reviews()
        st.rerun()

# Main area: one sample at a time
idx = st.session_state.idx
rec = sampled[idx]
sid = sample_id(rec)
existing = st.session_state.reviews.get(sid)

# Navigation row
nav_cols = st.columns([1, 1, 4, 1, 1])
with nav_cols[0]:
    if st.button("Prev", disabled=(idx == 0), use_container_width=True):
        st.session_state.idx = max(0, idx - 1)
        st.rerun()
with nav_cols[1]:
    if st.button("Next", disabled=(idx == len(sampled) - 1), use_container_width=True):
        st.session_state.idx = min(len(sampled) - 1, idx + 1)
        st.rerun()
with nav_cols[2]:
    jump = st.number_input(
        "Jump to sample #", min_value=1, max_value=len(sampled),
        value=idx + 1, label_visibility="collapsed",
    )
    if jump - 1 != idx:
        st.session_state.idx = jump - 1
        st.rerun()
with nav_cols[3]:
    next_unreviewed = next(
        (i for i in range(idx + 1, len(sampled)) if sample_id(sampled[i]) not in st.session_state.reviews),
        None,
    )
    if st.button("Next unrev.", disabled=(next_unreviewed is None), use_container_width=True):
        st.session_state.idx = next_unreviewed
        st.rerun()
with nav_cols[4]:
    st.markdown(f"**{idx + 1} / {len(sampled)}**")

st.markdown(
    f"**Stratum**: `{rec['_stratum']}` &nbsp;|&nbsp; "
    f"**Model**: `{rec['model']}` &nbsp;|&nbsp; "
    f"**Judge says detected**: `{rec['flaw_detected']}` "
    f"({rec['target_flaw_prominence']}) &nbsp;|&nbsp; "
    f"**Reviewed**: {'YES' if existing else 'no'}"
)

# Two-column layout: chart on left, evaluation context on right
left, right = st.columns([1, 1])

with left:
    img_path = CHARTS_DIR / rec["flaw_category"] / "png" / f"{rec['chart_name']}.png"
    if img_path.exists():
        st.image(str(img_path), caption=f"{rec['flaw_category']} / {rec['chart_name']}")
    else:
        st.warning(f"Image not found: {img_path}")

    st.markdown("**Ground truth**")
    st.markdown(f"- Flaw type: `{rec['flaw_category']}`")
    st.markdown(f"- Repetition: {rec['repetition']}")
    with st.expander("Ground-truth description", expanded=True):
        st.write(rec.get("ground_truth_description", "(none)"))

with right:
    st.markdown("**Judge verdict**")
    st.markdown(
        f"- `flaw_detected`: **{rec['flaw_detected']}**\n"
        f"- `target_flaw_prominence`: **{rec['target_flaw_prominence']}**\n"
        f"- `other_flaws_mentioned`: {rec.get('other_flaws_mentioned') or '[]'}"
    )
    with st.expander("Judge rationale", expanded=True):
        st.write(rec.get("rationale", "(none)"))

    with st.expander("Candidate (model) response", expanded=False):
        st.write(rec.get("candidate_response", "(none)"))

# Review form
st.divider()
st.subheader("Your review")

verdict_default = existing["human_verdict"] if existing else None
notes_default = existing["notes"] if existing else ""

verdict_options = ["correct", "incorrect", "unsure"]
verdict_index = verdict_options.index(verdict_default) if verdict_default in verdict_options else 0
verdict = st.radio(
    "Was the judge's `flaw_detected` decision correct?",
    options=verdict_options,
    index=verdict_index,
    horizontal=True,
    key=f"verdict_{sid}",
)
notes = st.text_area("Notes (optional)", value=notes_default, key=f"notes_{sid}", height=80)

submit_cols = st.columns([1, 1, 4])
with submit_cols[0]:
    if st.button("Save review", type="primary", use_container_width=True):
        st.session_state.reviews[sid] = {
            "sample_id": sid,
            "stratum": rec["_stratum"],
            "model": rec["model"],
            "flaw_category": rec["flaw_category"],
            "chart_name": rec["chart_name"],
            "repetition": rec["repetition"],
            "source_run_id": rec.get("source_run_id"),
            "judge_flaw_detected": rec["flaw_detected"],
            "judge_target_flaw_prominence": rec["target_flaw_prominence"],
            "human_verdict": verdict,
            "notes": notes,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        save_reviews(st.session_state.reviews)
        # Auto-advance to next unreviewed
        nxt = next(
            (i for i in range(idx + 1, len(sampled)) if sample_id(sampled[i]) not in st.session_state.reviews),
            None,
        )
        if nxt is not None:
            st.session_state.idx = nxt
        st.rerun()
with submit_cols[1]:
    if existing and st.button("Delete review", use_container_width=True):
        st.session_state.reviews.pop(sid, None)
        save_reviews(st.session_state.reviews)
        st.rerun()
