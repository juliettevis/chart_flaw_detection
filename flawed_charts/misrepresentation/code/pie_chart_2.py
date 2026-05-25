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

orders = df.drop_duplicates("Order ID")
counts = orders.groupby("Ship Mode").size().sort_values(ascending=False)

# Store original percentages for labels
original_total = counts.sum()
original_percentages = (counts.values / original_total) * 100

# Create modified values that don't match the labels
modified_values = [2000, 800, 1200, 300]  # These will create different visual proportions

fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts, autotexts = ax.pie(
    modified_values,  # Use modified values for visual encoding
    labels=None,
    autopct=lambda x: f"{original_percentages[modified_values.index(int(x * sum(modified_values) / 100))]:.1f}%",  # Show original percentages
    colors=PALETTE_WONG[1:len(counts) + 1],
    startangle=90,
    textprops={"fontsize": 14},
)
for t in autotexts:
    t.set_fontsize(13)

ax.legend(wedges, counts.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)
ax.set_title("Orders by Shipping Method (2023–2026)", fontsize=16, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()