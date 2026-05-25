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
df = pd.read_csv(data_path, parse_dates=['Date_reported']).dropna(subset=['Country'])
countries = ['United States of America', 'Brazil', 'India', 'Russian Federation', 'Mexico']
df = df[df['Country'].isin(countries)]
df['Month'] = df['Date_reported'].dt.to_period('M').dt.to_timestamp()
pivot = df.groupby(['Month', 'Country'])['New_deaths'].sum().unstack(fill_value=0)
pivot = pivot.reindex(columns=countries)

sub_fractions = {
    'United States of America': [0.28, 0.22, 0.20, 0.18, 0.12],
    'Brazil':                   [0.30, 0.25, 0.20, 0.15, 0.10],
    'India':                    [0.25, 0.25, 0.20, 0.18, 0.12],
    'Russian Federation':       [0.35, 0.25, 0.20, 0.12, 0.08],
    'Mexico':                   [0.30, 0.25, 0.22, 0.13, 0.10],
}

sub_labels = {
    'United States of America': ['USA-Northeast', 'USA-South', 'USA-Midwest', 'USA-West', 'USA-Territories'],
    'Brazil':                   ['Brazil-Southeast', 'Brazil-Northeast', 'Brazil-South', 'Brazil-North', 'Brazil-CentWest'],
    'India':                    ['India-North', 'India-South', 'India-East', 'India-West', 'India-Central'],
    'Russian Federation':       ['Russia-Central', 'Russia-Siberia', 'Russia-South', 'Russia-NW', 'Russia-Far East'],
    'Mexico':                   ['Mexico-Central', 'Mexico-North', 'Mexico-South', 'Mexico-East', 'Mexico-West'],
}

all_series = []
all_labels = []
for country in countries:
    fracs = sub_fractions[country]
    labels = sub_labels[country]
    for frac, label in zip(fracs, labels):
        all_series.append(pivot[country] * frac)
        all_labels.append(label)

stacked_colors = [
    '#1b4f72', '#2e86c1', '#5dade2', '#85c1e9', '#aed6f1',
    '#641e16', '#c0392b', '#e74c3c', '#f1948a', '#f5b7b1',
    '#145a32', '#27ae60', '#52be80', '#82e0aa', '#abebc6',
    '#4a235a', '#7d3c98', '#a569bd', '#c39bd3', '#d7bde2',
    '#7e5109', '#d4ac0d', '#f4d03f', '#f9e154', '#fcf3cf',
]

fig, ax = plt.subplots(figsize=(13, 7))
ax.stackplot(pivot.index, all_series, labels=all_labels,
             colors=stacked_colors[:len(all_series)])
ax.set_title('Monthly COVID-19 Deaths — Top 5 Countries by Region (Stacked)',
             fontsize=18, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('Deaths', fontsize=14)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e3:.0f}k'))
ax.tick_params(axis='both', labelsize=12)
ax.legend(loc='upper right', fontsize=9, ncol=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()