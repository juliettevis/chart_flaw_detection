import argparse, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'Housing.csv')
df = pd.read_csv(data_path)
prices = df['price'].dropna()

bin_edges = [1500000, 2500000, 3000000, 3500000, 4000000, 4500000, 5000000, 8000000, 13500000]

counts, _ = np.histogram(prices, bins=bin_edges)

bin_labels = []
for i in range(len(bin_edges) - 1):
    lo = bin_edges[i] / 1e6
    hi = bin_edges[i + 1] / 1e6
    bin_labels.append(f'€{lo:.1f}M-\n€{hi:.1f}M')

fig, ax = plt.subplots(figsize=(10, 6))

x_positions = np.arange(len(counts))
ax.bar(x_positions, counts, color=PALETTE_WONG[3], edgecolor='white', width=0.8)

ax.set_xticks(x_positions)
ax.set_xticklabels(bin_labels, fontsize=9)

ax.set_title('Distribution of House Prices', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Price (€)', fontsize=12)
ax.set_ylabel('Number of houses', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()