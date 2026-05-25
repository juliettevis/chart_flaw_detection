import argparse
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales = df.groupby("Sub-Category")["Sales"].sum().nlargest(8).sort_values(ascending=False)
total_sales = sales.sum()

# Only include top 5 categories in the pie chart
top5_sales = sales.head(5)
percentages = (top5_sales.values / total_sales * 100)

fig, ax = plt.subplots(figsize=(10, 6))

# Create pie chart with manual percentage labels
wedges, texts = ax.pie(top5_sales.values, labels=None, colors=PALETTE_WONG[:5], startangle=90)

# Add percentage labels to each slice
for i, (wedge, pct) in enumerate(zip(wedges, percentages)):
    angle = (wedge.theta1 + wedge.theta2) / 2
    x = wedge.r * 0.7 * np.cos(np.radians(angle))
    y = wedge.r * 0.7 * np.sin(np.radians(angle))
    ax.text(x, y, f'{pct:.1f}%', ha='center', va='center', fontsize=11, fontweight='bold')

ax.set_title("Total Sales by Top 8 Product Sub-Categories (2023–2026)", fontsize=14, fontweight="bold", pad=12)

# Add legend
ax.legend(wedges, top5_sales.index, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()