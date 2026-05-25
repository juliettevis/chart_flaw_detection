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
sub = df[df['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)'].copy()
sub = sub[~sub['Country'].str.contains('Total|Africa|America|Asia|Europe|Oceania', case=False, na=False)]

fig, ax = plt.subplots(figsize=(10, 6))
for country, grp in sub.groupby('Country'):
    grp = grp.sort_values('Year')
    if len(grp) >= 3:
        ax.plot(grp['Year'], grp['Value'], linewidth=0.7, alpha=0.5, color=PALETTE_WONG[5])

ax.set_title('CO₂ Emissions per Capita — All Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Metric tons CO₂ per person', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
ax.tick_params(axis='both', labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
