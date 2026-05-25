import argparse
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

orders = df.drop_duplicates("Order ID")
counts = orders.groupby(["Region", "Segment"]).size().unstack(fill_value=0)
regions = ["Central", "East", "South", "West"]
segments = ["Consumer", "Corporate", "Home Office"]
counts = counts.reindex(index=regions, columns=segments)

x = np.arange(len(regions))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))

deuteranopia_unfriendly_colors = ["#CC0000", "#009E73", "#E31A1C"]

for i, seg in enumerate(segments):
    ax.bar(x + i * width, counts[seg], width=width, label=seg, color=deuteranopia_unfriendly_colors[i])

ax.set_title("Order Count by Region and Customer Segment", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Region", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.set_xticks(x + width)
ax.set_xticklabels(regions)
ax.tick_params(axis="both", labelsize=10)
ax.legend(fontsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()