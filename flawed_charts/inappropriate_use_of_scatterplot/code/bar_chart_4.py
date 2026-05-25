import argparse
import sys
import os
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

fig, ax = plt.subplots(figsize=(10, 6))

# Create scatter plot with numeric x-positions
x_positions = range(len(counts))
ax.scatter(x_positions, counts.values, color=PALETTE_WONG[5], s=36)

# Add value labels
for i, (x, y) in enumerate(zip(x_positions, counts.values)):
    ax.text(x, y + 20, str(y), ha='center', fontsize=9)

ax.set_title("Number of FIFA 18 Players by Nationality (Top 10)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Nationality", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

# Set x-axis labels
ax.set_xticks(x_positions)
ax.set_xticklabels(counts.index, rotation=30, ha="right")

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()