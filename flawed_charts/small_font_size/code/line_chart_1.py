import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path, parse_dates=["Order Date"], dayfirst=True)

df = df[df["Order Date"].dt.year == 2025]
df["YearMonth"] = df["Order Date"].dt.to_period("M")
categories = ["Technology", "Office Supplies"]
pivot = df[df["Category"].isin(categories)].groupby(["YearMonth", "Category"])["Sales"].sum().unstack()
pivot = pivot.reindex(columns=categories)
dates = pivot.index.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 6))
for i, cat in enumerate(categories):
    ax.plot(dates, pivot[cat], color=PALETTE_WONG[i + 1], linewidth=1.5, marker="o", markersize=3, label=cat)

ax.set_title("Monthly Sales: Technology vs. Office Supplies (2025)", fontsize=5, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=4)
ax.set_ylabel("Sales ($)", fontsize=4)
ax.tick_params(axis="both", labelsize=3)
ax.set_xlim(dates[0] - pd.Timedelta(days=15), dates[-1] + pd.Timedelta(days=15))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(fontsize=3)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()