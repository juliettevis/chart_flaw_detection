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

fig, ax = plt.subplots(figsize=(10, 6))
sales_capped = df["Sales"][df["Sales"] <= 2000]
ax.hist(sales_capped, bins=20, color=PALETTE_WONG[1], edgecolor="white", linewidth=0.5)

ax.set_title("Distribution of Individual Order Sales (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Sales ($)", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

ax.invert_yaxis()
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

ax.spines["bottom"].set_visible(False)
ax.spines["top"].set_visible(True)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()