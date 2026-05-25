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

# Define bright categorical colors
categorical_colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'cyan', 'magenta', 
                     'brown', 'pink', 'lime', 'indigo', 'teal', 'coral', 'gold', 'navy']

for i, cat in enumerate(categories):
    # Plot each segment with a different categorical color
    for j in range(len(dates)):
        if j < len(dates) - 1:
            ax.plot(dates[j:j+2], pivot[cat].iloc[j:j+2], 
                   color=categorical_colors[j % len(categorical_colors)], 
                   linewidth=1.5, marker="o", markersize=4)
        else:
            ax.plot(dates[j], pivot[cat].iloc[j], 
                   color=categorical_colors[j % len(categorical_colors)], 
                   marker="o", markersize=4)
    
    # Add a dummy plot for legend
    ax.plot([], [], color='gray', linewidth=1.5, marker="o", markersize=4, label=cat)

ax.set_title("Quarterly Profit: Furniture vs. Technology (2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Quarter", fontsize=12)
ax.set_ylabel("Profit ($)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(dates[0] - pd.Timedelta(days=30), dates[-1] + pd.Timedelta(days=30))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Q{(mdates.num2date(x).month - 1) // 3 + 1} {mdates.num2date(x).year}"
))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(fontsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()