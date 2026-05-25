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

line1, = ax.plot(dates, pivot["Furniture"], color=PALETTE_IBM[0], linewidth=1.5, marker="o", markersize=4, label="Furniture")

ax2 = ax.twinx()
line2, = ax2.plot(dates, pivot["Technology"], color=PALETTE_IBM[1], linewidth=1.5, marker="o", markersize=4, label="Technology")

ax.set_title("Quarterly Profit: Furniture vs. Technology (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Quarter", fontsize=12)
ax.set_ylabel("Furniture Profit ($)", fontsize=12)
ax2.set_ylabel("Technology Profit ($)", fontsize=12)

ax.set_ylim(-2000, 5000)
ax2.set_ylim(-8000, 25000)

ax.tick_params(axis="both", labelsize=10)
ax2.tick_params(axis="both", labelsize=10)

ax.set_xlim(dates[0] - pd.Timedelta(days=30), dates[-1] + pd.Timedelta(days=30))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Q{(mdates.num2date(x).month - 1) // 3 + 1} {mdates.num2date(x).year}"
))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

lines = [line1, line2]
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, fontsize=10)

ax.spines["top"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()