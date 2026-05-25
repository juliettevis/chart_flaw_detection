import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data')

elec = pd.read_csv(os.path.join(data_dir,
    'electricity_production_from_renewable_sources_excluding_hydroelectric.csv'),
    skiprows=3)
year_cols = [c for c in elec.columns if c.isdigit()]
elec_last = elec[year_cols].apply(lambda r: r.dropna().iloc[-1] if r.notna().any() else None, axis=1)
elec_df = pd.DataFrame({'Country': elec['Country Name'], 'renewable_pct': elec_last}).dropna()
elec_df = elec_df[elec_df['renewable_pct'] >= 0]

co2 = pd.read_csv(os.path.join(data_dir, 'Carbon Dioxide_Emission_Estimates.csv'),
                  skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
co2['Value'] = pd.to_numeric(co2['Value'], errors='coerce')
co2 = co2[co2['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)']
co2_latest = co2.sort_values('Year').groupby('Country', as_index=False).tail(1)[['Country', 'Value']]
co2_latest = co2_latest.rename(columns={'Value': 'co2_pc'}).dropna()

merged = elec_df.merge(co2_latest, on='Country', how='inner')
merged = merged[merged['co2_pc'] <= 40]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(merged['renewable_pct'], merged['co2_pc'], color=PALETTE_WONG[3],
       alpha=0.6, width=0.4, edgecolor='none')
ax.set_title('Renewable Electricity Share vs. CO₂ per Capita (by country)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Renewable electricity (% of total, excl. hydro)', fontsize=12)
ax.set_ylabel('CO₂ per capita (t)', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()