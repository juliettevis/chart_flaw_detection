import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Carbon Dioxide_Emission_Estimates.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = df['Value'].astype(str).str.replace(',', '')
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
series = 'Emissions (thousand metric tons of carbon dioxide)'
latest = df[df['Series'] == series].copy()
latest_year = int(latest['Year'].max())
latest = latest[latest['Year'] == latest_year].dropna(subset=['Value'])
latest = latest[~latest['Country'].str.contains('Total|Africa|America|Asia|Europe|Oceania', case=False, na=False)]
latest = latest.set_index('Country')['Value']

china_total = latest.get('China', 0)
china_sectors = {
    'China — Industry': 0.45,
    'China — Power': 0.30,
    'China — Transport': 0.10,
    'China — Buildings': 0.08,
    'China — Other': 0.07,
}

top_others = latest.drop('China', errors='ignore').nlargest(4)

labels = list(china_sectors.keys()) + list(top_others.index)
values = [china_total * f for f in china_sectors.values()] + list(top_others.values)

colors = [PALETTE_WONG[5]] * len(labels)

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(labels, values, color=colors)

ax.set_title(f'CO₂ Emissions by Country/Sector ({latest_year})',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Thousand metric tons CO₂', fontsize=12)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
