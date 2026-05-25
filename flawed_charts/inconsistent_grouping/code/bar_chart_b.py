import argparse, sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Housing.csv')
df = pd.read_csv(data_path)
df = df[df['bedrooms'].isin([2, 3, 4])]

bed2_avg = df[df['bedrooms'] == 2]['price'].mean()
bed3_avg = df[df['bedrooms'] == 3]['price'].mean()
bed4_by_furn = df[df['bedrooms'] == 4].groupby('furnishingstatus')['price'].mean()

labels = ['2 bedrooms', '3 bedrooms'] + [f'4 bed — {s}' for s in bed4_by_furn.index]
values = [bed2_avg, bed3_avg] + list(bed4_by_furn.values)

colors = [PALETTE_WONG[5], PALETTE_WONG[2],
          PALETTE_WONG[1], PALETTE_WONG[0], PALETTE_WONG[6]]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(labels))
ax.bar(x, values, color=colors, width=0.6)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=20, ha='right')
ax.set_title('Average House Price by Bedrooms', fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Average price', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
