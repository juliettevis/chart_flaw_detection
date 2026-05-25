import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

fig, ax = plt.subplots(figsize=(10, 6))
bins = range(16, 44, 2)
counts, edges, patches = ax.hist(df["Age"], bins=bins, color=PALETTE_WONG[5], edgecolor="white", linewidth=0.5)
# Ensure main bars render in front of 3D face polygons
for patch in patches:
    patch.set_zorder(5)

# Add 3D effect to each bar
base_color = np.array(PALETTE_WONG[5])
dx = 0.3  # horizontal offset
for i, (count, patch) in enumerate(zip(counts, patches)):
    if count > 0:
        # Get bar position and dimensions
        x = patch.get_x()
        width = patch.get_width()
        height = patch.get_height()
        
        # Dynamic offset based on perspective (bars further right appear more offset)
        perspective_factor = 1 + (i / len(patches)) * 0.3
        dy = height * 0.03 * perspective_factor
        
        # Draw right side face (darker)
        right_face_x = [x + width, x + width + dx, x + width + dx, x + width]
        right_face_y = [0, 0, height + dy, height]
        ax.fill(right_face_x, right_face_y,
                color=base_color * 0.65,
                edgecolor='white', linewidth=0.3, zorder=2)

        # Draw top face (lighter)
        top_face_x = [x, x + width, x + width + dx, x + dx]
        top_face_y = [height, height, height + dy, height + dy]
        ax.fill(top_face_x, top_face_y,
                color=np.minimum(base_color * 1.1, 1.0),
                edgecolor='white', linewidth=0.3, zorder=3)
        # Re-assert main bar on top
        patch.set_zorder(5)

ax.set_title("Distribution of FIFA 18 Player Ages", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age (years)", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()