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
df = df.dropna(subset=['Age', 'Wage (€)'])

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['Age'], df['Wage (€)'], color=PALETTE_WONG[5], alpha=0.6, s=8, edgecolors='none')

# Add misleading trend line
z = np.polyfit(df['Age'], df['Wage (€)'], 1)
p = np.poly1d(z)
x_trend = np.linspace(15, df['Age'].max(), 100)
ax.plot(x_trend, p(x_trend), color=PALETTE_WONG[0], linewidth=2.5, alpha=0.9)

ax.set_title("Age vs Wage of FIFA 18 Players", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age", fontsize=12)
ax.set_ylabel("Wage (€)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(left=15)
ax.set_ylim(bottom=0)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x/1000:.0f}K"))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()