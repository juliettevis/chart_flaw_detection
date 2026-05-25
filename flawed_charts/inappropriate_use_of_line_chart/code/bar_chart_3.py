import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(dates, monthly.values, color=PALETTE_CUSTOM[0], marker='o', linewidth=2, markersize=6)

ax.set_title("Number of Orders per Month (2025)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Number of Orders", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(dates[0] - pd.Timedelta(days=20), dates[-1] + pd.Timedelta(days=20))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()