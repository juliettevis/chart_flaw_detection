import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path, parse_dates=["Order Date"], dayfirst=True)

df["Quarter"] = df["Order Date"].dt.to_period("Q")
categories = ["Technology", "Office Supplies", "Furniture"]
pivot = df.groupby(["Quarter", "Category"])["Sales"].sum().unstack()
pivot = pivot.reindex(columns=categories).fillna(0)
dates = pivot.index.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 6))
ax.stackplot(dates, [pivot[c] for c in categories], labels=categories, colors=PALETTE_CUSTOM[:len(categories)])

ax.set_title("Quarterly Sales by Product Category (Stacked, 2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Quarter", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(dates[0] - pd.Timedelta(days=30), dates[-1] + pd.Timedelta(days=30))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Q{(mdates.num2date(x).month - 1) // 3 + 1} {mdates.num2date(x).year}"
))

ax.set_yscale('log')
ax.set_ylim(1, 5000000)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=10, borderaxespad=0)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()