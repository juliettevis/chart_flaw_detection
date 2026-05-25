import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data')

co2 = pd.read_csv(os.path.join(data_dir, 'Carbon Dioxide_Emission_Estimates.csv'),
                  skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
co2['Value'] = pd.to_numeric(co2['Value'], errors='coerce')
co2 = co2[co2['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)']
co2_latest = co2.sort_values('Year').groupby('Country', as_index=False).tail(1)[['Country', 'Value']]
co2_latest = co2_latest.rename(columns={'Value': 'co2_pc'}).dropna()

wom = pd.read_csv(os.path.join(data_dir, 'Seats_held_by_women_in_Parliament.csv'),
                  skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
wom['Value'] = pd.to_numeric(wom['Value'], errors='coerce')
wom_latest = wom.sort_values('Year').groupby('Country', as_index=False).tail(1)[['Country', 'Value']]
wom_latest = wom_latest.rename(columns={'Value': 'women_pct'}).dropna()

merged = co2_latest.merge(wom_latest, on='Country', how='inner')
merged = merged[merged['co2_pc'] <= 40]

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(merged['women_pct'], merged['co2_pc'], color=PALETTE_WONG[5],
           alpha=0.6, s=40, edgecolors='none')

x = merged['women_pct'].values
y = merged['co2_pc'].values
coeffs = np.polyfit(x, y, 1)
slope, intercept = coeffs[0], coeffs[1]
steep_slope = slope * 3.0
x_line = np.linspace(x.min(), x.max(), 200)
y_line = steep_slope * x_line + intercept
ax.plot(x_line, y_line, color='crimson', linewidth=2.5)

ax.set_title('Women in Parliament vs. CO₂ per Capita (by country)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('% seats held by women', fontsize=12)
ax.set_ylabel('CO₂ emissions per capita (t)', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()