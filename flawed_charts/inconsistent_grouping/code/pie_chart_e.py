import argparse, sys, os
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
df['Value'] = df['Value'].astype(str).str.replace(',', '')
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

pop = df[df['Series'] == 'Population mid-year estimates (millions)'].copy()
latest = pop.sort_values('Year').groupby('Country', as_index=False).tail(1)

asia_sub = {
    'Eastern Asia': latest[latest['Country'] == 'Eastern Asia']['Value'].values,
    'Southern Asia': latest[latest['Country'] == 'Southern Asia']['Value'].values,
    'South-eastern Asia': latest[latest['Country'] == 'South-eastern Asia']['Value'].values,
    'Western Asia': latest[latest['Country'] == 'Western Asia']['Value'].values,
}

other_continents = {
    'Africa': latest[latest['Country'] == 'Africa']['Value'].values,
    'Europe': latest[latest['Country'] == 'Europe']['Value'].values,
    'Americas': latest[latest['Country'] == 'Americas']['Value'].values,
    'Oceania': latest[latest['Country'] == 'Oceania']['Value'].values,
}

labels = []
sizes = []
for k, v in asia_sub.items():
    if len(v) > 0:
        labels.append(k)
        sizes.append(float(v[0]))
for k, v in other_continents.items():
    if len(v) > 0:
        labels.append(k)
        sizes.append(float(v[0]))

colors = ['#c0392b', '#e74c3c', '#f1948a', '#f5b7b1',
          PALETTE_WONG[5], PALETTE_WONG[2], PALETTE_WONG[3], PALETTE_WONG[1]]

fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(sizes)],
                                   autopct='%1.1f%%', startangle=140, pctdistance=0.75)
for t in autotexts:
    t.set_fontsize(9)

ax.set_title('World Population by Region', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
