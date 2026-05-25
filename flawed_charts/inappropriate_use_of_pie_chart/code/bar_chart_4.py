import argparse
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

counts = df['Nationality'].value_counts().head(10)
total_all_players = df.shape[0]  # Total of all players in the dataset

# Only show top 4 countries in the pie chart
top_4_counts = counts.head(4)

# Calculate percentages based on the TOTAL dataset, not just the pie slices
percentages = (top_4_counts.values / total_all_players * 100)

fig, ax = plt.subplots(figsize=(10, 8))

# Create pie chart with manual percentage labels
wedges, texts = ax.pie(top_4_counts.values, labels=None, colors=PALETTE_WONG[:4], startangle=90, radius=0.75)

# Add percentage labels manually to avoid auto-normalization
for i, (wedge, pct) in enumerate(zip(wedges, percentages)):
    angle = (wedge.theta1 + wedge.theta2) / 2
    x = wedge.r * 0.7 * np.cos(np.radians(angle))
    y = wedge.r * 0.7 * np.sin(np.radians(angle))
    ax.text(x, y, f'{pct:.1f}%', ha='center', va='center', fontsize=12, fontweight='bold')

# Add legend with country names
ax.legend(wedges, top_4_counts.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=11)

ax.set_title("Number of FIFA 18 Players by Nationality (Top 10)", fontsize=14, fontweight="bold", pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()