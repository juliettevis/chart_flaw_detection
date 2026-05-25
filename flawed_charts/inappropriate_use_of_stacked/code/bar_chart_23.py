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
                         'Population_Surface_Area_and_Density.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

countries = ['Japan', 'Germany', 'Brazil', 'India', 'Nigeria', 'United States of America']
young_series = 'Population aged 0 to 14 years old (percentage)'
old_series = 'Population aged 60+ years old (percentage)'

def latest(country, series):
    s = df[(df['Country'] == country) & (df['Series'] == series)].dropna(subset=['Value'])
    return s.sort_values('Year').iloc[-1]['Value']

rows = []
for c in countries:
    y = latest(c, young_series)
    o = latest(c, old_series)
    rows.append({'Country': c, 'young': y, 'old': o, 'middle': 100 - y - o})

data = pd.DataFrame(rows)
x = np.arange(len(countries))

# Split each of the 3 original age groups into 4 sub-groups => 12 stacked layers
sub_labels = [
    '0–3', '4–7', '8–11', '12–14',
    '15–24', '25–34', '35–44', '45–59',
    '60–64', '65–69', '70–74', '75+'
]

# Split fractions for each group
young_splits = [0.27, 0.27, 0.27, 0.19]
middle_splits = [0.22, 0.25, 0.28, 0.25]
old_splits = [0.20, 0.22, 0.28, 0.30]

rainbow_colors = [
    '#e6194b', '#f58231', '#ffe119', '#bfef45',
    '#3cb44b', '#42d4f4', '#4363d8', '#911eb4',
    '#f032e6', '#a9a9a9', '#9A6324', '#800000'
]

fig, ax = plt.subplots(figsize=(13, 7))

bottoms = np.zeros(len(countries))
layer_idx = 0

for i, frac in enumerate(young_splits):
    vals = data['young'].values * frac
    ax.bar(x, vals, bottom=bottoms, color=rainbow_colors[layer_idx], label=sub_labels[layer_idx])
    bottoms += vals
    layer_idx += 1

for i, frac in enumerate(middle_splits):
    vals = data['middle'].values * frac
    ax.bar(x, vals, bottom=bottoms, color=rainbow_colors[layer_idx], label=sub_labels[layer_idx])
    bottoms += vals
    layer_idx += 1

for i, frac in enumerate(old_splits):
    vals = data['old'].values * frac
    ax.bar(x, vals, bottom=bottoms, color=rainbow_colors[layer_idx], label=sub_labels[layer_idx])
    bottoms += vals
    layer_idx += 1

ax.set_xticks(x)
ax.set_xticklabels(countries, rotation=20, ha='right')
ax.set_title('Population by Age Bracket — 6 Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('% of population', fontsize=12)
ax.legend(fontsize=8, ncol=2, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()