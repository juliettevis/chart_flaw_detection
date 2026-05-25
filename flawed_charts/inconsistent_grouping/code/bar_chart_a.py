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
                         'superstore.csv')
df = pd.read_csv(data_path)

tech_subs = df[df['Category'] == 'Technology'].groupby('Sub-Category')['Profit'].sum()
furn_total = df[df['Category'] == 'Furniture']['Profit'].sum()
office_total = df[df['Category'] == 'Office Supplies']['Profit'].sum()

labels = list(tech_subs.index) + ['Furniture', 'Office Supplies']
values = list(tech_subs.values) + [furn_total, office_total]

colors = [PALETTE_WONG[0], PALETTE_WONG[1], PALETTE_WONG[2], PALETTE_WONG[3],
          PALETTE_WONG[5], PALETTE_WONG[6]]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(labels))
ax.bar(x, values, color=colors, width=0.6)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=30, ha='right')
ax.set_title('Profit by Category (Superstore)', fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Profit ($)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}k'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
