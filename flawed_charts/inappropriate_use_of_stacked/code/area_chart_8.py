import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'WHO-COVID-19-global-data.csv')
df = pd.read_csv(data_path, parse_dates=['Date_reported']).dropna(subset=['WHO_region'])
df = df[df['WHO_region'] != 'OTHER']
df['Month'] = df['Date_reported'].dt.to_period('M').dt.to_timestamp()
regions = sorted(df['WHO_region'].unique())
region_names = {
    'AFRO': 'African Region',
    'AMRO': 'Region of the Americas',
    'EMRO': 'Eastern Mediterranean Region',
    'EURO': 'European Region',
    'SEARO': 'South-East Asia Region',
    'WPRO': 'Western Pacific Region',
}
pivot = df.groupby(['Month', 'WHO_region'])['New_cases'].sum().unstack(fill_value=0)
pivot = pivot.reindex(columns=regions)

# Split each region into sub-series
sub_fractions = [0.28, 0.22, 0.18, 0.17, 0.15]
sub_labels_template = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']

all_series = []
all_labels = []
all_colors = []

rainbow_colors = [
    '#e6194b', '#f58231', '#ffe119', '#bfef45', '#3cb44b',
    '#42d4f4', '#4363d8', '#911eb4', '#f032e6', '#a9a9a9',
    '#9A6324', '#469990', '#800000', '#aaffc3', '#000075',
    '#dcbeff', '#fffac8', '#ffd8b1', '#e6beff', '#fabebe',
    '#aaaaff', '#ffaaaa', '#aaffaa', '#ffddaa', '#ddaaff',
    '#aaddff', '#ffaadd', '#ccffaa', '#ffccaa', '#aaccff',
]

color_idx = 0
for r in regions:
    base_values = pivot[r].values
    for i, (frac, sublabel) in enumerate(zip(sub_fractions, sub_labels_template)):
        series = base_values * frac
        all_series.append(series)
        all_labels.append(f'{region_names[r]} – {sublabel}')
        all_colors.append(rainbow_colors[color_idx % len(rainbow_colors)])
        color_idx += 1

fig, ax = plt.subplots(figsize=(13, 7))
ax.stackplot(pivot.index, all_series,
             labels=all_labels,
             colors=all_colors)
ax.set_title('Monthly COVID-19 New Cases by WHO Region (Jan 2020 – Mar 2026)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('New cases', fontsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M'))
ax.legend(loc='upper left', fontsize=6, ncol=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()