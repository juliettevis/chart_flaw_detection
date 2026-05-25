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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales = df.groupby("Sub-Category")["Sales"].sum().nlargest(8).sort_values(ascending=False)

base_width = 0.6
min_width = 0.2
max_width = 0.9
relative_widths = sales.values / sales.values.max()
bar_widths = min_width + relative_widths * (max_width - min_width)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(sales.index, sales.values, color=PALETTE_WONG[1], width=bar_widths)

ax.set_title("Total Sales by Top 8 Product Sub-Categories (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Sub-Category", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()