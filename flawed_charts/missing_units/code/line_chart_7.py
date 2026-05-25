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
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
sub = df[(df['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)') &
         (df['Country'] == 'China')].dropna(subset=['Value']).sort_values('Year')

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sub['Year'], sub['Value'], color=PALETTE_WONG[6],
        linewidth=2, marker='o', markersize=5)
ax.set_title('China — CO₂ Emissions per Capita',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Emissions per Capita', fontsize=12)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()