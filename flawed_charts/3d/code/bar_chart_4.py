import argparse
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

counts = df['Nationality'].value_counts().head(10)

fig, ax = plt.subplots(figsize=(10, 6))

base_color = PALETTE_WONG[5]

# Parse base color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def scale_color(rgb, factor):
    return tuple(min(1.0, max(0.0, c * factor)) for c in rgb)

base_rgb = hex_to_rgb(base_color)
dark_rgb = scale_color(base_rgb, 0.65)
light_rgb = scale_color(base_rgb, 1.10)

bar_width = 0.6
dx = 0.18  # horizontal offset for 3D effect

# Draw bars with 3D effect
bars = ax.bar(counts.index, counts.values, color=base_color, width=bar_width, zorder=3)

# Get x positions from the bars
x_positions = [bar.get_x() for bar in bars]
bar_widths = [bar.get_width() for bar in bars]

for i, (bar, val) in enumerate(zip(bars, counts.values)):
    x_left = bar.get_x()
    x_right = bar.get_x() + bar.get_width()
    y_bottom = 0
    y_top = val
    dy = val * 0.03  # vertical offset for 3D effect

    # Right side face
    right_face_x = [x_right, x_right + dx, x_right + dx, x_right, x_right]
    right_face_y = [y_bottom, y_bottom + dy, y_top + dy, y_top, y_bottom]
    ax.fill(right_face_x, right_face_y, color=dark_rgb, edgecolor='white', linewidth=0.3, zorder=4)

    # Top face
    top_face_x = [x_left, x_right, x_right + dx, x_left + dx, x_left]
    top_face_y = [y_top, y_top, y_top + dy, y_top + dy, y_top]
    ax.fill(top_face_x, top_face_y, color=light_rgb, edgecolor='white', linewidth=0.3, zorder=4)

# Add bar labels
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width() / 2, val + val * 0.03 + 20,
            str(int(val)), ha='center', va='bottom', fontsize=9)

ax.set_title("Number of FIFA 18 Players by Nationality (Top 10)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Nationality", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()