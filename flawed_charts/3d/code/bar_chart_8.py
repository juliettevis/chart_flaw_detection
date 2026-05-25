import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

fig, ax = plt.subplots(figsize=(10, 6))
sales_capped = df["Sales"][df["Sales"] <= 2000]

# Create histogram data
counts, bins, patches = ax.hist(sales_capped, bins=20, color=PALETTE_WONG[1], edgecolor="white", linewidth=0.5)
# Main bars must render in front of 3D face polygons
for patch in patches:
    patch.set_zorder(5)

# Add 3D effect to each bar
base_color = np.array([230/255, 159/255, 0/255])  # PALETTE_WONG[1] color
dx = 15  # horizontal offset for 3D effect
for i, (patch, count) in enumerate(zip(patches, counts)):
    # Get bar dimensions
    x = patch.get_x()
    width = patch.get_width()
    height = patch.get_height()
    
    # Calculate perspective-based offset (bars on the right appear "closer")
    perspective_factor = 1 + (i / len(patches)) * 0.3
    dy = height * 0.03 * perspective_factor
    
    # Draw right side face (darker) — behind main bar
    right_face_color = base_color * 0.65
    right_face = plt.Polygon([
        (x + width, 0),
        (x + width + dx, dy),
        (x + width + dx, height + dy),
        (x + width, height)
    ], facecolor=right_face_color, edgecolor='white', linewidth=0.3, zorder=2)
    ax.add_patch(right_face)

    # Draw top face (lighter) — behind main bar
    top_face_color = np.minimum(base_color * 1.1, 1.0)
    top_face = plt.Polygon([
        (x, height),
        (x + width, height),
        (x + width + dx, height + dy),
        (x + dx, height + dy)
    ], facecolor=top_face_color, edgecolor='white', linewidth=0.3, zorder=3)
    ax.add_patch(top_face)

ax.set_title("Distribution of Individual Order Sales (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Sales ($)", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()