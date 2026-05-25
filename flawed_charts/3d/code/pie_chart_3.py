import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, PathPatch
from matplotlib.path import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

# Map preferred positions to position groups
def position_group(pos_str):
    if pd.isna(pos_str):
        return None
    first_pos = pos_str.strip().split()[0]
    if first_pos == 'GK':
        return 'Goalkeeper'
    elif first_pos in ('CB', 'LB', 'RB', 'LWB', 'RWB', 'LCB', 'RCB'):
        return 'Defender'
    elif first_pos in ('CM', 'CDM', 'CAM', 'LM', 'RM', 'LCM', 'RCM', 'LDM', 'RDM'):
        return 'Midfielder'
    else:
        return 'Forward'

df['Position Group'] = df['Preferred Positions'].apply(position_group)
counts = df['Position Group'].dropna().value_counts()

# Order: Forward, Midfielder, Defender, Goalkeeper
order = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
counts = counts.reindex(order)

fig, ax = plt.subplots(figsize=(10, 6))

# Parameters for 3D effect
depth = 0.18
squash_factor = 0.5

# Calculate angles
sizes = counts.values
angles = np.cumsum([0] + list(sizes / np.sum(sizes) * 360))
angles_rad = np.radians(angles)

# Draw cylinder sides
for i in range(len(sizes)):
    start_angle = angles_rad[i]
    end_angle = angles_rad[i+1]
    
    # Draw cylinder side for bottom-facing parts
    n_segments = 40
    angle_range = np.linspace(start_angle, end_angle, n_segments)
    
    for j in range(len(angle_range) - 1):
        a1 = angle_range[j]
        a2 = angle_range[j+1]
        
        # Only draw bottom-facing segments
        if np.sin((a1 + a2) / 2) < 0.05:
            # Create quad for cylinder side
            x1, y1 = np.cos(a1), np.sin(a1) * squash_factor
            x2, y2 = np.cos(a2), np.sin(a2) * squash_factor
            
            quad = np.array([
                [x1, y1 - depth],
                [x2, y2 - depth],
                [x2, y2],
                [x1, y1]
            ])
            
            # Calculate shading based on angle
            angle_norm = ((a1 + a2) / 2) % (2 * np.pi)
            shade_factor = 0.4 + 0.3 * np.abs(np.cos(angle_norm))
            
            # Get base color and apply shading
            base_color = plt.cm.colors.to_rgb(PALETTE_IBM[i])
            shaded_color = tuple(c * shade_factor for c in base_color)
            
            ax.add_patch(Polygon(quad, facecolor=shaded_color, edgecolor='none'))

# Draw top pie face as ellipse
for i in range(len(sizes)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    
    # Create elliptical wedge
    theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    x = np.cos(theta)
    y = np.sin(theta) * squash_factor
    
    # Add center point
    x = np.concatenate([[0], x, [0]])
    y = np.concatenate([[0], y, [0]])
    
    vertices = np.column_stack([x, y])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    
    path = Path(vertices, codes)
    patch = PathPatch(path, facecolor=PALETTE_IBM[i], edgecolor='none')
    ax.add_patch(patch)

# Add percentage labels
for i in range(len(sizes)):
    angle = (angles[i] + angles[i+1]) / 2
    x = np.cos(np.radians(angle)) * 0.7
    y = np.sin(np.radians(angle)) * 0.7 * squash_factor
    
    percentage = sizes[i] / np.sum(sizes) * 100
    ax.text(x, y, f"{percentage:.1f}%", ha='center', va='center', fontsize=13)

# Create legend
legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=PALETTE_IBM[i], edgecolor='none', label=counts.index[i]) 
                  for i in range(len(counts))]
ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-0.8, 0.8)
ax.set_aspect('equal')
ax.axis('off')

ax.set_title("Distribution of Players by Position Group", fontsize=16, fontweight="bold", pad=16, y=0.95)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()