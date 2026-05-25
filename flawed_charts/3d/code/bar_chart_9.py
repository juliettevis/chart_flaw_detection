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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

col = "Estimated prevalence of TB (all forms) per 100 000 population"
data_2013 = df[df["Year"] == 2013][col].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
bins = range(0, 1050, 50)

# Create histogram data
counts, bin_edges = np.histogram(data_2013, bins=bins)
bin_width = bin_edges[1] - bin_edges[0]

# Base color
base_color = PALETTE_WONG[3]
base_rgb = plt.cm.colors.to_rgb(base_color)

# 3D offset parameters
dx = 8
dy_factor = 0.03

for i, (count, bin_start) in enumerate(zip(counts, bin_edges[:-1])):
    if count > 0:
        # Draw main bar
        bar = ax.bar(bin_start, count, width=bin_width, color=base_color, 
                      edgecolor='white', linewidth=0.3, align='edge')
        
        # Calculate dynamic offset based on height
        dy = count * dy_factor
        
        # Draw right side face (darker)
        right_x = [bin_start + bin_width, bin_start + bin_width + dx, 
                   bin_start + bin_width + dx, bin_start + bin_width]
        right_y = [0, 0, count + dy, count]
        darker_color = tuple(c * 0.65 for c in base_rgb)
        ax.fill(right_x, right_y, color=darker_color, edgecolor='white', linewidth=0.3)
        
        # Draw top face (lighter)
        top_x = [bin_start, bin_start + bin_width, 
                 bin_start + bin_width + dx, bin_start + dx]
        top_y = [count, count, count + dy, count + dy]
        lighter_color = tuple(min(c * 1.1, 1.0) for c in base_rgb)
        ax.fill(top_x, top_y, color=lighter_color, edgecolor='white', linewidth=0.3)

ax.set_title("Distribution of TB Prevalence Rates Across Countries (2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("TB Prevalence per 100,000 Population", fontsize=12)
ax.set_ylabel("Number of Countries", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

# Adjust x-axis to account for 3D effect
ax.set_xlim(-20, 1050)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()