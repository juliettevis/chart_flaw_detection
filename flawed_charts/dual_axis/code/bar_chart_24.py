import argparse, sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Seats_held_by_women_in_Parliament.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

y10 = df[df['Year'] == 2010].dropna(subset=['Value']).set_index('Country')['Value']
y25 = df[df['Year'] == 2025].dropna(subset=['Value']).set_index('Country')['Value']
top = y25.nlargest(10).index
vals_10 = [y10.get(c, 0) for c in top]
vals_25 = [y25.get(c, 0) for c in top]

x = np.arange(len(top))
width = 0.38

fig, ax = plt.subplots(figsize=(11, 6))

bar1 = ax.bar(x - width/2, vals_10, width, color=PALETTE_WONG[5], label='2010')
ax.set_xticks(x)
ax.set_xticklabels(top, rotation=30, ha='right')
ax.set_title('Women in National Parliament — Top 10 Countries (2010 vs 2025)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('2010 — % seats held by women', fontsize=12)
ax.set_ylim(0, 60)
ax.spines['top'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

ax2 = ax.twinx()
bar2 = ax2.bar(x + width/2, vals_25, width, color=PALETTE_WONG[1], label='2025')
ax2.set_ylabel('2025 — % seats held by women', fontsize=12)
ax2.set_ylim(0, 80)
ax2.spines['top'].set_visible(False)

handles1, labels1 = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax.legend(handles1 + handles2, labels1 + labels2, fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()