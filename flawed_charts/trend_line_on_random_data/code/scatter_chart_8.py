import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'Housing.csv')
df = pd.read_csv(data_path).dropna(subset=['price', 'area'])

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['area'], df['price'], color=PALETTE_WONG[1],
           alpha=0.6, s=30, edgecolors='none')

coeffs = np.polyfit(df['area'], df['price'], 1)
poly = np.poly1d(coeffs)
x_line = np.linspace(df['area'].min(), df['area'].max(), 300)
ax.plot(x_line, poly(x_line), color='crimson', linewidth=2.5, linestyle='-', label='Trend')

ax.set_title('House Price vs. House Area', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Area (sq ft)', fontsize=12)
ax.set_ylabel('Price (€)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x/1e6:.1f}M'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()