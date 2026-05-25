import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Path, PathPatch
from matplotlib.transforms import Affine2D

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

# Custom colors for 6 regions — avoids the two similar purples in PALETTE_CUSTOM
COLORS_6 = [
    PALETTE_CUSTOM[0],                     # Blue
    PALETTE_CUSTOM[1],                     # Orange
    PALETTE_CUSTOM[2],                     # Red
    (0, 158/255, 115/255),                 # Teal (from Wong palette)
    PALETTE_CUSTOM[4],                     # Gray
    (180/255, 130/255, 40/255),            # Dark gold
]

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

region_labels = {
    "AFR": "Africa", "SEA": "South-East Asia", "EMR": "Eastern Mediterranean",
    "WPR": "Western Pacific", "EUR": "Europe", "AMR": "Americas"
}

deaths_2013 = df[df["Year"] == 2013].groupby("Region")[
    "Estimated number of deaths from TB (all forms, excluding HIV)"
].sum()
deaths_2013 = deaths_2013.rename(index=region_labels)
deaths_2013 = deaths_2013.sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(11, 8))

# 3D cylinder parameters
depth = 0.18
squash = 0.5

# Calculate angles and values
values = deaths_2013.values
total = values.sum()
sizes = values / total * 360
angles = np.zeros(len(sizes) + 1)
for i in range(1, len(sizes) + 1):
    angles[i] = angles[i-1] + sizes[i-1]
angles = np.deg2rad(angles + 90)

# Draw cylinder sides
for i in range(len(values)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    
    # Only draw visible part (bottom-facing)
    n_segments = 50
    angle_range = np.linspace(start_angle, end_angle, n_segments)
    
    for j in range(len(angle_range) - 1):
        angle1 = angle_range[j]
        angle2 = angle_range[j+1]
        
        # Check if this segment is visible (bottom-facing)
        mid_angle = (angle1 + angle2) / 2
        if np.sin(mid_angle) < 0.05:
            # Create quad for cylinder side
            x1 = np.cos(angle1)
            y1 = np.sin(angle1) * squash
            x2 = np.cos(angle2)
            y2 = np.sin(angle2) * squash
            
            quad_x = [x1, x2, x2, x1]
            quad_y = [y1, y2, y2 - depth, y1 - depth]
            
            # Lighting effect based on angle
            light_factor = 0.4 + 0.6 * (1 - abs(np.cos(mid_angle)))
            color = tuple(c * light_factor for c in COLORS_6[i][:3])
            
            ax.fill(quad_x, quad_y, color=color, edgecolor='none')

# Draw top pie face as elliptical wedges
for i in range(len(values)):
    start_angle = angles[i]
    end_angle = angles[i+1]
    
    # Create elliptical wedge path
    theta = np.linspace(start_angle, end_angle, 100)
    x = np.cos(theta)
    y = np.sin(theta) * squash
    
    # Close the wedge
    x = np.concatenate([[0], x, [0]])
    y = np.concatenate([[0], y, [0]])
    
    vertices = list(zip(x, y))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(vertices, codes)
    patch = PathPatch(path, facecolor=COLORS_6[i], edgecolor='none')
    ax.add_patch(patch)

# Add percentage labels
for i in range(len(values)):
    mid_angle = (angles[i] + angles[i+1]) / 2
    pct = values[i] / total * 100
    
    # Position for labels
    if pct < 5:  # Small slices
        label_r = 1.15
        ha = 'center'
    else:
        label_r = 0.75
        ha = 'center'
    
    x = label_r * np.cos(mid_angle)
    y = label_r * np.sin(mid_angle) * squash
    
    ax.text(x, y, f'{pct:.1f}%', ha=ha, va='center', fontsize=13)

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.2, 1.2)
ax.set_aspect('equal')
ax.axis('off')

ax.set_title("Share of Global TB Deaths by WHO Region (2013)", fontsize=16, fontweight="bold", pad=16)
ax.legend([plt.Rectangle((0,0),1,1, fc=COLORS_6[i]) for i in range(len(deaths_2013))], 
          deaths_2013.index, title="Region", loc="center left",
          bbox_to_anchor=(1.0, 0.5), fontsize=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()