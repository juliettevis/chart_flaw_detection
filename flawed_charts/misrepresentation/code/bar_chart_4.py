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

# Store original values for labels
original_values = counts.values.copy()

# Create misrepresented values for plotting
misrepresented_values = counts.values.copy()
misrepresented_values[0] = 900  # England: 1630 → 900
misrepresented_values[1] = 1500  # Germany: 1140 → 1500
misrepresented_values[2] = 700  # Spain: 1019 → 700
misrepresented_values[3] = 1200  # France: 978 → 1200
misrepresented_values[4] = 600  # Argentina: 965 → 600
misrepresented_values[5] = 1100  # Brazil: 812 → 1100
misrepresented_values[6] = 500  # Italy: 799 → 500
misrepresented_values[7] = 900  # Colombia: 592 → 900
misrepresented_values[8] = 300  # Japan: 469 → 300
misrepresented_values[9] = 800  # Netherlands: 429 → 800

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(counts.index, misrepresented_values, color=PALETTE_WONG[5], width=0.6)

# Use original values for labels
ax.bar_label(bars, labels=[str(int(val)) for val in original_values], fmt="%s", fontsize=9, padding=3)

ax.set_title("Number of FIFA 18 Players by Nationality (Top 10)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Nationality", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()