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

# Plot Consumer and Corporate on primary y-axis
ax.bar(x + 0 * width, counts["Consumer"], width=width, label="Consumer", color=PALETTE_IBM[0])
ax.bar(x + 1 * width, counts["Corporate"], width=width, label="Corporate", color=PALETTE_IBM[1])

# Create secondary y-axis for Home Office
ax2 = ax.twinx()
ax2.bar(x + 2 * width, counts["Home Office"], width=width, label="Home Office", color=PALETTE_IBM[2])

# Set misleading y-axis limits so Home Office bars appear to closely track Consumer/Corporate
# Consumer ranges ~450-840, Corporate ~250-490, Home Office ~130-310
# Primary axis: 0 to 900
ax.set_ylim(0, 1000)
# Secondary axis: scale it so Home Office (130-310) visually overlaps with Consumer/Corporate
ax2.set_ylim(0, 400)

ax.set_title("Order Count by Region and Customer Segment", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Region", fontsize=12)
ax.set_ylabel("Consumer & Corporate (Number of Orders)", fontsize=12)
ax2.set_ylabel("Home Office (Number of Orders)", fontsize=12)

ax.set_xticks(x + width)
ax.set_xticklabels(regions)
ax.tick_params(axis="both", labelsize=10)
ax2.tick_params(axis="both", labelsize=10)

# Combine legends
handles1, labels1 = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax.legend(handles1 + handles2, labels1 + labels2, fontsize=10, loc="upper right")

ax.spines["top"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()