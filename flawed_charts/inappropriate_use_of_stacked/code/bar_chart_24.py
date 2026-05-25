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

# Split each year's values into 5 sub-groups each, giving 10 stacked layers total
np.random.seed(42)

def split_into_parts(values, n_parts):
    result = []
    for v in values:
        cuts = np.sort(np.random.dirichlet(np.ones(n_parts)) * v)
        result.append(cuts)
    return np.array(result).T  # shape: (n_parts, n_countries)

sub_labels_10 = ['2010-Urban', '2010-Rural', '2010-North', '2010-South', '2010-Central']
sub_labels_25 = ['2025-Urban', '2025-Rural', '2025-North', '2025-South', '2025-Central']

parts_10 = split_into_parts(vals_10, 5)
parts_25 = split_into_parts(vals_25, 5)

x = np.arange(len(top))

rainbow_colors = [
    '#e6194b', '#f58231', '#ffe119', '#3cb44b', '#42d4f4',
    '#4363d8', '#911eb4', '#f032e6', '#a9a9a9', '#800000',
    '#9a6324', '#469990'
]

fig, ax = plt.subplots(figsize=(14, 7))

bottom_10 = np.zeros(len(top))
bottom_25 = np.zeros(len(top))

width = 0.38

for i, (label, part) in enumerate(zip(sub_labels_10, parts_10)):
    ax.bar(x - width/2, part, width, bottom=bottom_10, color=rainbow_colors[i], label=label)
    bottom_10 += part

for i, (label, part) in enumerate(zip(sub_labels_25, parts_25)):
    ax.bar(x + width/2, part, width, bottom=bottom_25, color=rainbow_colors[i+5], label=label)
    bottom_25 += part

ax.set_xticks(x)
ax.set_xticklabels(top, rotation=30, ha='right')
ax.set_title('Women in National Parliament — Top 10 Countries (2010 vs 2025)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('% seats held by women', fontsize=12)
ax.legend(fontsize=7, ncol=2, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()