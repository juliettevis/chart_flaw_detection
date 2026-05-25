import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)
df = df.dropna(subset=['Age', 'Wage (€)'])
df['Wage (€)'] = df['Wage (€)'].clip(lower=1)  # plot zero-wage players at €1 on log scale

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['Age'], df['Wage (€)'], color=PALETTE_WONG[5], alpha=0.6, s=8, edgecolors='none')

ax.set_title("Age vs Wage of FIFA 18 Players", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age", fontsize=12)
ax.set_ylabel("Wage (€)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(left=15)
ax.set_yscale('log')
ax.set_ylim(bottom=1)

def format_func(value, tick_number):
    if value >= 1000:
        return f"€{value:,.0f}"
    else:
        return f"€{value:.0f}"

ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_func))
ax.yaxis.set_major_locator(mticker.LogLocator(base=10.0, numticks=15))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()