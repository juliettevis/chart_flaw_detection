import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path, parse_dates=["Order Date"], dayfirst=True)

df["Quarter"] = df["Order Date"].dt.to_period("Q")
categories = ["Furniture", "Technology"]
pivot = df[df["Category"].isin(categories)].groupby(["Quarter", "Category"])["Profit"].sum().unstack()
pivot = pivot.reindex(columns=categories)
dates = pivot.index.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 6))
for i, cat in enumerate(categories):
    ax.plot(dates, pivot[cat], color=PALETTE_IBM[i], linewidth=1.5, marker="o", markersize=4, label=cat)

ax.set_title("Quarterly Profit: Furniture vs. Technology (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Quarter", fontsize=12)
ax.set_ylabel("Profit ($)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(dates[0] - pd.Timedelta(days=30), dates[-1] + pd.Timedelta(days=30))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Q{(mdates.num2date(x).month - 1) // 3 + 1} {mdates.num2date(x).year}"
))

# Get current y-tick positions
yticks = ax.get_yticks()
# Create inconsistent y-tick labels
ylabels = []
for i, tick in enumerate(yticks):
    if i % 4 == 0:
        ylabels.append(f"${tick:,.0f}")
    elif i % 4 == 1:
        ylabels.append(f"{tick:.0f}")
    elif i % 4 == 2:
        ylabels.append(f"${tick/1000:.0f}K")
    else:
        ylabels.append(f"{tick:,.2f}")
ax.set_yticks(yticks)
ax.set_yticklabels(ylabels)

ax.legend(fontsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()