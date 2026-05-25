import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Carbon Dioxide_Emission_Estimates.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
sub = df[(df['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)') &
         (df['Region/Country/Area'] != 1)]
latest_year = int(sub['Year'].max())
latest = sub[sub['Year'] == latest_year].dropna(subset=['Value'])
top = latest.nlargest(15, 'Value').sort_values('Value', ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(top['Country'], top['Value'], color=PALETTE_WONG[6], marker='o', linewidth=2, markersize=6)
ax.set_title(f'Top 15 CO₂ Emitters per Capita ({latest_year})',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Country', fontsize=12)
ax.set_ylabel('CO₂ emissions per capita (t)', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()