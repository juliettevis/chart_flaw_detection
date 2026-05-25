import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path, parse_dates=["Order Date"], dayfirst=True)
df = df[df["Order Date"].dt.year == 2025]
df["YearMonth"] = df["Order Date"].dt.to_period("M")
monthly = df.groupby("YearMonth")["Order ID"].nunique().sort_index()
dates = monthly.index.to_timestamp()

labels = [d.strftime("%b %Y") for d in dates]
values = monthly.values

scrambled_order = [6, 11, 2, 8, 0, 4, 9, 1, 7, 3, 10, 5]
scrambled_labels = [labels[i] for i in scrambled_order]
scrambled_values = [values[i] for i in scrambled_order]

x = np.arange(len(scrambled_labels))

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x, scrambled_values, width=0.6, color=PALETTE_CUSTOM[0])

ax.set_title("Number of Orders per Month (2025)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(scrambled_labels, rotation=45, ha="right", fontsize=10)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()