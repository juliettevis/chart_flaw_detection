import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales_by_region = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)

# Store original percentages for labels
original_values = sales_by_region.values
original_percentages = (original_values / original_values.sum()) * 100

# Create misrepresented values for plotting
misrepresented_values = [sales_by_region.values[0] * 0.5,  # West: much smaller than 31.8%
                        sales_by_region.values[1] * 1.4,   # East: larger than 29.7%
                        sales_by_region.values[2] * 0.8,   # Central: smaller than 21.6%
                        sales_by_region.values[3] * 1.5]   # South: much larger than 16.8%

# Sort the misrepresented values to maintain color consistency
sorted_indices = sorted(range(len(misrepresented_values)), key=lambda i: misrepresented_values[i], reverse=True)
sorted_misrepresented = [misrepresented_values[i] for i in sorted_indices]
sorted_regions = [sales_by_region.index[i] for i in sorted_indices]

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    sorted_misrepresented,
    labels=None,
    autopct=lambda pct: f"{original_percentages[sorted_indices[sorted_misrepresented.index(pct * sum(sorted_misrepresented) / 100)]]:.1f}%",
    colors=PALETTE_WONG[:len(sales_by_region)],
    startangle=90,
    pctdistance=0.75
)

for t in autotexts:
    t.set_fontsize(13)

ax.set_title("Sales Distribution by Region (2023–2026)", fontsize=16, fontweight="bold", pad=16)
ax.legend(wedges, sorted_regions, title="Region", loc="center left",
          bbox_to_anchor=(0.92, 0.5), fontsize=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()