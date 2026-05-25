import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.path import Path
import matplotlib.patches as patches

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 8))

# 3D parameters
depth = 0.18
squash = 0.5

# Calculate percentages
percentages = sales.values / sales.sum() * 100
angles = np.cumsum(np.concatenate(([0], percentages * 360 / 100)))

# Draw cylinder sides first (behind the top face)
for i in range(len(sales)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    color = PALETTE_IBM[i]
    
    # Draw cylinder side using many small quads
    angle_steps = max(int((end_angle - start_angle) / 2), 10)
    for j in range(angle_steps):
        a1 = np.radians(start_angle + j * (end_angle - start_angle) / angle_steps)
        a2 = np.radians(start_angle + (j+1) * (end_angle - start_angle) / angle_steps)
        
        # Only draw bottom-facing parts
        if np.sin(a1) < 0.05 or np.sin(a2) < 0.05:
            x1, y1 = np.cos(a1), np.sin(a1) * squash
            x2, y2 = np.cos(a2), np.sin(a2) * squash
            
            # Create quad for cylinder side
            quad = np.array([
                [x1, y1 - depth],
                [x2, y2 - depth],
                [x2, y2],
                [x1, y1]
            ])
            
            # Shade based on angle for cylindrical effect
            shade_factor = 0.3 + 0.7 * (1 - abs(np.cos((a1 + a2) / 2)))
            rgb = plt.matplotlib.colors.to_rgb(color)
            shaded_color = tuple(c * shade_factor for c in rgb)
            
            ax.add_patch(Polygon(quad, facecolor=shaded_color, edgecolor='none'))

# Draw top elliptical pie face
for i in range(len(sales)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    color = PALETTE_IBM[i]
    
    # Create elliptical wedge using Path
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    x = np.concatenate(([0], np.cos(theta), [0]))
    y = np.concatenate(([0], np.sin(theta) * squash, [0]))
    
    verts = list(zip(x, y))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]
    path = Path(verts, codes)
    
    patch = patches.PathPatch(path, facecolor=color, edgecolor='none')
    ax.add_patch(patch)
    
    # Add percentage labels
    mid_angle = np.radians((start_angle + end_angle) / 2)
    label_x = 0.7 * np.cos(mid_angle)
    label_y = 0.7 * np.sin(mid_angle) * squash
    ax.text(label_x, label_y, f"{percentages[i]:.1f}%", 
            ha='center', va='center', fontsize=13, weight='normal')

# Set aspect and limits
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.2, 1.2)
ax.set_aspect('equal')
ax.axis('off')

# Add legend
legend_elements = [plt.Rectangle((0, 0), 1, 1, fc=PALETTE_IBM[i]) for i in range(len(sales))]
ax.legend(legend_elements, sales.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

ax.set_title("Sales Distribution by Product Category (2023–2026)", fontsize=16, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()