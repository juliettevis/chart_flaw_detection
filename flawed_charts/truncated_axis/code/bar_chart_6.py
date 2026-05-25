import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

top10 = (df[df["Year"] == 2013]
         .nlargest(10, "Estimated prevalence of TB (all forms) per 100 000 population")
         .set_index("Country or territory name")
         ["Estimated prevalence of TB (all forms) per 100 000 population"]
         .sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(range(len(top10)), top10.values, color=PALETTE_WONG[0], width=0.6)

for bar, val in zip(bars, top10.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
            f"{val:.0f}", ha="center", va="bottom", fontsize=9)

ax.set_xticks(range(len(top10)))
ax.set_xticklabels(top10.index, rotation=35, ha="right", fontsize=9)
ax.set_title("Top 10 Countries by TB Prevalence per 100,000 (2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Country", fontsize=12)
ax.set_ylabel("Prevalence per 100,000", fontsize=12)
ax.tick_params(axis="y", labelsize=10)

ax.set_ylim(400, 1000)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()