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
bars = ax.bar(counts.index, counts.values, color=PALETTE_WONG[5], width=0.6)

ax.bar_label(bars, fmt="%d", fontsize=9, padding=3)

ax.set_title("Number of FIFA 18 Players by Nationality (Top 10)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Nationality", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

ax.set_ylim(300, 1700)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()