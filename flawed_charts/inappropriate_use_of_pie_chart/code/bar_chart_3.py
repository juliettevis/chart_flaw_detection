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

# Only include top 5 months in pie chart
top_5_indices = monthly.nlargest(5).index
top_5_values = monthly[top_5_indices].values
top_5_labels = [idx.strftime("%b %Y") for idx in top_5_indices]

# Calculate percentages relative to the FULL total (all 12 months)
total_orders = monthly.sum()
percentages = [(val/total_orders)*100 for val in top_5_values]

# Create pie chart with manual percentage labels
wedges, texts = ax.pie(top_5_values,
                        labels=[f"{pct:.1f}%" for pct in percentages],
                        colors=PALETTE_CUSTOM[:5],
                        startangle=90,
                        counterclock=False,
                        textprops={'fontsize': 10})

ax.legend(wedges, top_5_labels, title="Month", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

ax.set_title("Number of Orders per Month (2025)", fontsize=14, fontweight="bold", pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()