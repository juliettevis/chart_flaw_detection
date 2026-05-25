import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge, Path, PathPatch
import matplotlib.colors

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales_by_region = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 8))

# 3D parameters
depth = 0.18
y_scale = 0.5  # Squash factor for ellipse

# Calculate angles
sizes = sales_by_region.values
total = sum(sizes)
angles = np.cumsum([0] + [size/total * 360 for size in sizes])

# Draw cylinder sides first (only for bottom-facing parts)
for i in range(len(sizes)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    color = PALETTE_WONG[i % len(PALETTE_WONG)]
    
    # Draw many small quads for the cylinder side
    num_steps = max(int((end_angle - start_angle) / 2), 10)
    for j in range(num_steps):
        angle1 = np.radians(start_angle + j * (end_angle - start_angle) / num_steps)
        angle2 = np.radians(start_angle + (j + 1) * (end_angle - start_angle) / num_steps)
        
        # Only draw if facing downward
        if np.sin(angle1) < 0.05 or np.sin(angle2) < 0.05:
            x1, y1 = np.cos(angle1), np.sin(angle1) * y_scale
            x2, y2 = np.cos(angle2), np.sin(angle2) * y_scale
            
            # Quad vertices
            vertices = [(x1, y1), (x2, y2), (x2, y2 - depth), (x1, y1 - depth)]
            
            # Lighting based on angle (darker at bottom, lighter at sides)
            shade_factor = 0.4 + 0.3 * abs(np.cos((angle1 + angle2) / 2))
            r, g, b = matplotlib.colors.to_rgb(color)
            shaded_color = (r * shade_factor, g * shade_factor, b * shade_factor)
            
            quad = plt.Polygon(vertices, facecolor=shaded_color, edgecolor='none')
            ax.add_patch(quad)

# Draw top elliptical pie slices
for i in range(len(sizes)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    color = PALETTE_WONG[i % len(PALETTE_WONG)]
    
    # Create elliptical wedge using Path
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    r = 1
    x = r * np.cos(theta)
    y = r * np.sin(theta) * y_scale
    
    # Add center point and close path
    vertices = [(0, 0)] + list(zip(x, y)) + [(0, 0)]
    codes = [Path.MOVETO] + [Path.LINETO] * len(theta) + [Path.CLOSEPOLY]
    
    path = Path(vertices, codes)
    patch = PathPatch(path, facecolor=color, edgecolor='none')
    ax.add_patch(patch)

# Add percentage labels
for i in range(len(sizes)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    mid_angle = (start_angle + end_angle) / 2
    
    # Calculate label position
    label_r = 0.75
    x = label_r * np.cos(np.radians(mid_angle))
    y = label_r * np.sin(np.radians(mid_angle)) * y_scale
    
    percentage = sizes[i] / total * 100
    ax.text(x, y, f'{percentage:.1f}%', ha='center', va='center', fontsize=13)

ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-0.8 - depth, 0.8)
ax.set_aspect('equal')
ax.axis('off')

ax.text(0, 0.9, "Sales Distribution by Region (2023–2026)", 
        fontsize=16, fontweight="bold", ha='center', transform=ax.transAxes)

# Create legend
legend_elements = []
for i, region in enumerate(sales_by_region.index):
    color = PALETTE_WONG[i % len(PALETTE_WONG)]
    legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, label=region))

ax.legend(handles=legend_elements, title="Region", loc="center left",
          bbox_to_anchor=(0.92, 0.5), fontsize=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()