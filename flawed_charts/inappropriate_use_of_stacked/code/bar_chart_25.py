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
pivot = df.groupby(['bedrooms', 'furnishingstatus'])['price'].mean().unstack()
pivot = pivot[['furnished', 'semi-furnished', 'unfurnished']]

# Approximate values from the chart:
# 2 bed: furnished~4.15M, semi~4.0M, unfurnished~3.07M
# 3 bed: furnished~5.48M, semi~5.05M, unfurnished~4.47M
# 4 bed: furnished~6.98M, semi~5.57M, unfurnished~4.27M

categories = ['2 bedrooms', '3 bedrooms', '4 bedrooms']

story_labels = ['1 story', '2 stories', '3 stories', '4 stories']
furnishing_types = ['furnished', 'semi-furnished', 'unfurnished']

sub_labels = []
sub_values = []

for furn in furnishing_types:
    furn_df = df[df['furnishingstatus'] == furn]
    for s in [1, 2, 3, 4]:
        avg = furn_df[furn_df['stories'] == s].groupby('bedrooms')['price'].mean()
        avg = avg.reindex([2, 3, 4], fill_value=0)
        sub_labels.append(f'{furn.capitalize()} — {story_labels[s-1]}')
        sub_values.append(avg.values)

# Rainbow palette with 12 colors
rainbow_colors = [
    '#e6194b', '#f58231', '#ffe119', '#bfef45',
    '#3cb44b', '#42d4f4', '#4363d8', '#911eb4',
    '#f032e6', '#a9a9a9', '#9A6324', '#469990'
]

x = np.arange(len(categories))
width = 0.5

fig, ax = plt.subplots(figsize=(13, 7))

bottoms = np.zeros(len(categories))
for idx, (label, vals) in enumerate(zip(sub_labels, sub_values)):
    ax.bar(x, vals, width, bottom=bottoms, color=rainbow_colors[idx % len(rainbow_colors)], label=label)
    bottoms += vals

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_title('Average House Price by Bedrooms and Furnishing Status',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Average price (€)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'€{x/1e6:.1f}M'))
ax.legend(fontsize=7, ncol=2, loc='upper left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()