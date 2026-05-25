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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales = df.groupby("Sub-Category")["Sales"].sum().nlargest(8).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(sales))
bar_width = 0.6
dx = 0.12
dy_factor = 0.03

base_color = np.array(plt.cm.colors.to_rgba(PALETTE_WONG[1]))
side_color = np.clip(base_color * np.array([0.65, 0.65, 0.65, 1.0]), 0, 1)
top_color = np.clip(base_color * np.array([1.1, 1.1, 1.1, 1.0]), 0, 1)

for i, (cat, val) in enumerate(sales.items()):
    dy = val * dy_factor
    left = x[i] - bar_width / 2
    right = x[i] + bar_width / 2

    ax.bar(x[i], val, width=bar_width, color=PALETTE_WONG[1], zorder=2, edgecolor='white', linewidth=0.3)

    side_x = [right, right, right + dx, right + dx]
    side_y = [0, val, val + dy, dy]
    ax.fill(side_x, side_y, color=side_color, zorder=2, edgecolor='white', linewidth=0.3)

    top_x = [left, right, right + dx, left + dx]
    top_y = [val, val, val + dy, val + dy]
    ax.fill(top_x, top_y, color=top_color, zorder=3, edgecolor='white', linewidth=0.3)

ax.set_title("Total Sales by Top 8 Product Sub-Categories (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Sub-Category", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(sales.index, rotation=30, ha="right")
ax.tick_params(axis="both", labelsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
