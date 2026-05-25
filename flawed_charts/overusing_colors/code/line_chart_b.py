import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d/%m/%Y", errors="coerce")
df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()

pivot = df.groupby(["Month", "Sub-Category"])["Sales"].sum().unstack(fill_value=0)
cmap = plt.get_cmap("tab20")

fig, ax = plt.subplots(figsize=(11, 6))
for i, col in enumerate(pivot.columns):
    ax.plot(pivot.index, pivot[col], color=cmap(i % 20), linewidth=1.5, label=col)

ax.set_title("Monthly Sales by Sub-Category (Superstore)", fontsize=14, fontweight="bold")
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
ax.legend(fontsize=8, ncol=3, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
