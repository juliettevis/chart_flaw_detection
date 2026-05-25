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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

df = df.dropna(subset=['Value (€)', 'Overall'])
df = df[df['Overall'] >= 80]

fig, ax = plt.subplots(figsize=(10, 6))

# Define categorical colors for sequential data
categorical_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 
                     'olive', 'cyan', 'magenta', 'yellow', 'navy', 'teal', 'lime']

# Color each point based on its Overall rating
unique_ratings = sorted(df['Overall'].unique())
color_map = {rating: categorical_colors[i % len(categorical_colors)] for i, rating in enumerate(unique_ratings)}

for rating in unique_ratings:
    mask = df['Overall'] == rating
    ax.scatter(df[mask]['Overall'], df[mask]['Value (€)'], 
              color=color_map[rating], alpha=0.6, s=30, edgecolors='none')

ax.set_title("Player Market Value vs Overall Rating by Position", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Overall Rating", fontsize=12)
ax.set_ylabel("Market Value (€)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_ylim(bottom=0)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"\u20ac{x/1e6:.0f}M"))
ax.set_xticks(range(int(df['Overall'].min()), int(df['Overall'].max()) + 1))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()