import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.colors

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

orders = df.drop_duplicates("Order ID")
counts = orders.groupby("Ship Mode").size().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))

# 3D pie parameters
squash = 0.5  # vertical squashing factor
depth = 0.18  # depth of the cylinder

# Calculate angles for each slice
values = counts.values
total = sum(values)
angles = []
cumsum = 0
for val in values:
    angles.append((cumsum * 360 / total, (cumsum + val) * 360 / total))
    cumsum += val

colors = PALETTE_WONG[1:len(counts) + 1]

# Draw cylinder sides (only for bottom-facing parts)
for i, (start_angle, end_angle) in enumerate(angles):
    # Draw multiple quads for smooth cylinder appearance
    n_segments = int((end_angle - start_angle) * 2)  # More segments for larger slices
    n_segments = max(n_segments, 10)
    
    for j in range(n_segments):
        angle1 = np.radians(start_angle + j * (end_angle - start_angle) / n_segments)
        angle2 = np.radians(start_angle + (j + 1) * (end_angle - start_angle) / n_segments)
        
        # Only draw if facing downward (bottom half)
        if np.sin((angle1 + angle2) / 2) < 0.05:
            x1, y1 = np.cos(angle1), np.sin(angle1) * squash
            x2, y2 = np.cos(angle2), np.sin(angle2) * squash
            
            # Create quad for cylinder side
            quad = Polygon([
                [x1, y1 - depth],
                [x2, y2 - depth],
                [x2, y2],
                [x1, y1]
            ], closed=True)
            
            # Vary shading based on angle for cylindrical effect
            shade_factor = 0.6 + 0.3 * np.abs(np.cos((angle1 + angle2) / 2))
            color_rgb = matplotlib.colors.to_rgb(colors[i])
            shaded_color = tuple(c * shade_factor for c in color_rgb)
            
            quad.set_facecolor(shaded_color)
            quad.set_edgecolor('none')
            ax.add_patch(quad)

# Draw top face of pie
for i, (start_angle, end_angle) in enumerate(angles):
    # Create elliptical wedge using Path
    theta1 = np.radians(start_angle)
    theta2 = np.radians(end_angle)
    
    # Generate points along the arc
    n_points = max(int((end_angle - start_angle) / 2), 20)
    theta = np.linspace(theta1, theta2, n_points)
    
    # Create elliptical arc points
    x = np.cos(theta)
    y = np.sin(theta) * squash
    
    # Create path for wedge
    verts = [(0, 0)]  # Center
    verts.extend(list(zip(x, y)))  # Arc points
    verts.append((0, 0))  # Close at center
    
    codes = [Path.MOVETO]
    codes.extend([Path.LINETO] * (len(verts) - 2))
    codes.append(Path.CLOSEPOLY)
    
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor=colors[i], edgecolor='none')
    ax.add_patch(patch)

# Add percentage labels
for i, (start_angle, end_angle) in enumerate(angles):
    mid_angle = np.radians((start_angle + end_angle) / 2)
    label_r = 0.7
    x = label_r * np.cos(mid_angle)
    y = label_r * np.sin(mid_angle) * squash
    
    percentage = values[i] / total * 100
    ax.text(x, y, f"{percentage:.1f}%", ha='center', va='center', fontsize=13)

# Add legend with category names
legend_patches = [patches.Patch(color=colors[i], label=counts.index[i]) for i in range(len(counts))]
ax.legend(handles=legend_patches, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-0.8, 0.8)
ax.set_aspect('equal')
ax.axis('off')

ax.set_title("Orders by Shipping Method (2023–2026)", fontsize=16, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()