import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

fig, ax = plt.subplots(figsize=(10, 8))

# Create sales ranges and count orders in each range
sales_ranges = [
    (r'\$0-\$100', df[(df['Sales'] >= 0) & (df['Sales'] < 100)].shape[0]),
    (r'\$100-\$250', df[(df['Sales'] >= 100) & (df['Sales'] < 250)].shape[0]),
    (r'\$250-\$500', df[(df['Sales'] >= 250) & (df['Sales'] < 500)].shape[0]),
    (r'\$500-\$1000', df[(df['Sales'] >= 500) & (df['Sales'] < 1000)].shape[0]),
]

# Calculate total number of ALL orders (not just those in our ranges)
total_orders = len(df)

# Extract values and labels for the top 4 ranges only
labels = [r[0] for r in sales_ranges]
values = [r[1] for r in sales_ranges]

# Calculate percentages based on TOTAL orders (including those not shown)
percentages = [(v / total_orders) * 100 for v in values]

# Create custom labels with percentages
percentage_labels = [f'{p:.1f}%' for p in percentages]

# Create pie chart (no outer labels — shown in legend)
wedges, texts = ax.pie(values, labels=None,
                        colors=PALETTE_WONG[:len(values)],
                        startangle=90, radius=0.8)

# Manually add percentage labels
for i, (wedge, pct) in enumerate(zip(wedges, percentage_labels)):
    angle = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
    x = wedge.r * 0.7 * np.cos(np.radians(angle))
    y = wedge.r * 0.7 * np.sin(np.radians(angle))
    ax.text(x, y, pct, ha='center', va='center', fontsize=12, fontweight='bold')

ax.set_title("Distribution of Individual Order Sales by Price Category (2023-2026)", fontsize=14, fontweight="bold", pad=12)

# Add legend
ax.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()