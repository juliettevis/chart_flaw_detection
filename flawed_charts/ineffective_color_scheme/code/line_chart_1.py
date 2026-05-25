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

# Define bright categorical colors for each month
categorical_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow']

for i, cat in enumerate(categories):
    # Plot each line segment with different colors
    for j in range(len(dates) - 1):
        ax.plot(dates[j:j+2], pivot[cat].iloc[j:j+2], color=categorical_colors[j], linewidth=1.5, marker="o", markersize=3)
    # Add the last point
    ax.plot(dates[-1], pivot[cat].iloc[-1], color=categorical_colors[-1], marker="o", markersize=3)
    # Add label only once for legend
    ax.plot([], [], color='black', linewidth=1.5, marker="o", markersize=3, label=cat)

ax.set_title("Monthly Sales: Technology vs. Office Supplies (2025)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(dates[0] - pd.Timedelta(days=15), dates[-1] + pd.Timedelta(days=15))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(fontsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()