"""
Demo: Why mpl_toolkits.mplot3d is not used for the 3D flaw injection.

mpl_toolkits.mplot3d renders bars in a true 3D perspective projection,
which causes two problems:
  1. The perspective distortion changes bar heights depending on viewing
     angle, making comparisons inaccurate in ways unrelated to the flaw.
  2. The z-axis and depth dimension introduce visual complexity that has
     nothing to do with the intended flaw (unjustified use of 3D on
     inherently 2D data).

The polygon-based approach used in the actual pipeline adds a shallow 3D
appearance without any perspective distortion, keeping the focus on the
flaw itself.
"""

import argparse
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
PALETTE_IBM = [
    (100/255, 143/255, 1.0),             # Blue
    (1.0, 176/255, 0),                   # Yellow
    (254/255, 97/255, 0),               # Orange
    (220/255, 38/255, 127/255),          # Pink
    (120/255, 94/255, 240/255),          # Purple
]
parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..', '..', '..', 'data', 'superstore.csv'
)

df = pd.read_csv(data_path)
orders = df.drop_duplicates("Order ID")
counts = orders.groupby(["Region", "Segment"]).size().unstack(fill_value=0)

regions = ["Central", "East", "South", "West"]
segments = ["Consumer", "Corporate", "Home Office"]
counts = counts.reindex(index=regions, columns=segments)

fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection='3d')

x_base = np.arange(len(regions))
width = 0.2
depth = 0.2

for i, seg in enumerate(segments):
    values = counts[seg].values
    ax.bar3d(
        x_base + i * width,    # x position
        i * depth,             # y position (depth)
        np.zeros(len(regions)),# z base (floor)
        width,                 # dx
        depth,                 # dy
        values,                # dz = height
        color=PALETTE_IBM[i],
        alpha=0.85,
        label=seg
    )

ax.set_title(
    "Order Count by Region and Customer Segment",
    fontsize=14,
    fontweight="bold",
    pad=16
)
ax.set_xlabel("Region", fontsize=10, labelpad=10)
ax.set_ylabel("Segment", fontsize=10, labelpad=10)
ax.set_zlabel("Number of Orders", fontsize=10, labelpad=10)

ax.set_xticks(x_base + width)
ax.set_xticklabels(regions, fontsize=9)
ax.set_yticks([])  # y-axis has no meaningful labels here

ax.legend(fontsize=9, loc='upper left')

# NOTE: the viewing angle heavily affects perceived bar heights.
# Rotating this plot (or changing elev/azim) changes which bars
# look taller, which is the core problem with mplot3d for this flaw.
ax.view_init(elev=25, azim=-60)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300, bbox_inches='tight')
plt.close()