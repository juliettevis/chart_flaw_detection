import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

region_order = ["AFR", "SEA", "EMR", "WPR", "EUR", "AMR"]
region_labels = {
    "AFR": "Africa", "SEA": "South-East Asia", "EMR": "Eastern Mediterranean",
    "WPR": "Western Pacific", "EUR": "Europe", "AMR": "Americas"
}

pivot = df.groupby(["Year", "Region"])["Estimated number of incident cases (all forms)"].sum().unstack()
pivot = pivot.reindex(columns=region_order).fillna(0)
pivot = pivot.rename(columns=region_labels)

# Apply cumulative sum to each region
for region_label in region_labels.values():
    pivot[region_label] = pivot[region_label].cumsum()

years = pivot.index.values

fig, ax = plt.subplots(figsize=(10, 6))
ax.stackplot(years, [pivot[region_labels[r]] for r in region_order],
             labels=[region_labels[r] for r in region_order],
             colors=PALETTE_CUSTOM[:len(region_order)])

ax.set_title("Estimated TB Incidence by WHO Region (1990–2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Incident Cases", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
ax.legend(loc="upper left", fontsize=9)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()