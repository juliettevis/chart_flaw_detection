import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data')

crime = pd.read_csv(os.path.join(data_dir, 'Intentional_homicides_and_other_crimes.csv'),
                    skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
crime['Value'] = pd.to_numeric(crime['Value'], errors='coerce')
crime = crime[crime['Series'] == 'Intentional homicide rates per 100,000']
crime_latest = crime.sort_values('Year').groupby('Country', as_index=False).tail(1)[['Country', 'Value']]
crime_latest = crime_latest.rename(columns={'Value': 'homicide'}).dropna()

pop = pd.read_csv(os.path.join(data_dir, 'Population_Surface_Area_and_Density.csv'),
                  skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
pop['Value'] = pd.to_numeric(pop['Value'], errors='coerce')
pop = pop[pop['Series'] == 'Population density']
pop_latest = pop.sort_values('Year').groupby('Country', as_index=False).tail(1)[['Country', 'Value']]
pop_latest = pop_latest.rename(columns={'Value': 'density'}).dropna()

merged = crime_latest.merge(pop_latest, on='Country', how='inner')
merged = merged[(merged['density'] <= 1000) & (merged['homicide'] <= 80)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(merged['density'], merged['homicide'], color=PALETTE_WONG[6],
           alpha=0.6, s=40, edgecolors='none')

x = merged['density'].values
y = merged['homicide'].values
coeffs = np.polyfit(x, y, 1)
poly = np.poly1d(coeffs)
x_line = np.linspace(x.min(), x.max(), 300)
ax.plot(x_line, poly(x_line), color='crimson', linewidth=2.5, solid_capstyle='round')

ax.set_title('Homicide Rate vs. Population Density (by country)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Population density (per km²)', fontsize=12)
ax.set_ylabel('Homicides per 100,000', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()