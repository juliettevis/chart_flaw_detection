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

# Split each segment into 4 sub-segments
sub_segments = []
data_dict = {}
colors = [plt.get_cmap("tab20")(i) for i in range(20)]

for seg in segments:
    for i in range(4):
        sub_seg_name = f"{seg}_{i+1}"
        sub_segments.append(sub_seg_name)
        # Divide the original values roughly equally among sub-segments
        data_dict[sub_seg_name] = counts[seg] / 4 + np.random.randint(-5, 5, size=len(regions))

# Create DataFrame with all sub-segments
stacked_df = pd.DataFrame(data_dict, index=regions)

# Create stacked bar chart
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(regions))
width = 0.6

# Create bottom tracker for stacking
bottom = np.zeros(len(regions))

# Stack all 12 layers
for i, col in enumerate(stacked_df.columns):
    ax.bar(x, stacked_df[col], width=width, bottom=bottom, 
           label=col, color=colors[i % len(colors)])
    bottom += stacked_df[col]

ax.set_title("Order Count by Region and Customer Segment", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Region", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(regions)
ax.tick_params(axis="both", labelsize=10)
ax.legend(fontsize=8, ncol=2, loc='upper right')

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()