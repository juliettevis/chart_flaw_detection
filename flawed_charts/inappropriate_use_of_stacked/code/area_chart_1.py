import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np

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

# Create sub-categories for each main category
sub_categories = []
sub_data = []
sub_labels = []
colors = []

# Define sub-category names and color palette
tech_subs = ["Computers", "Phones", "Accessories", "Peripherals"]
office_subs = ["Paper", "Binders", "Pens", "Storage", "Labels"]
furniture_subs = ["Chairs", "Tables", "Bookcases", "Cabinets"]

# Extended color palette for many layers (matplotlib tab20 qualitative)
extended_colors = [plt.get_cmap("tab20")(i) for i in range(20)]

color_idx = 0
for cat, subcats in [("Technology", tech_subs), ("Office Supplies", office_subs), ("Furniture", furniture_subs)]:
    cat_data = pivot[cat].values
    # Distribute the category total among subcategories with some variation
    n_subs = len(subcats)
    for i, subcat in enumerate(subcats):
        # Create uneven distribution
        if i == 0:
            fraction = 0.35
        elif i == 1:
            fraction = 0.25
        elif i == 2:
            fraction = 0.20
        elif i == 3:
            fraction = 0.15
        else:
            fraction = 0.05
        
        sub_data.append(cat_data * fraction)
        sub_labels.append(f"{cat} - {subcat}")
        colors.append(extended_colors[color_idx % len(extended_colors)])
        color_idx += 1

fig, ax = plt.subplots(figsize=(10, 6))
ax.stackplot(dates, sub_data, labels=sub_labels, colors=colors[:len(sub_data)])

ax.set_title("Quarterly Sales by Product Category (Stacked, 2023–2026)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Quarter", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(dates[0] - pd.Timedelta(days=30), dates[-1] + pd.Timedelta(days=30))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"Q{(mdates.num2date(x).month - 1) // 3 + 1} {mdates.num2date(x).year}"
))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(loc="upper left", fontsize=8, ncol=2)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()