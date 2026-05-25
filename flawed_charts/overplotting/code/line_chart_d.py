import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'electricity_production_from_renewable_sources_excluding_hydroelectric.csv')
df = pd.read_csv(data_path, skiprows=3)
years = [str(y) for y in range(1990, 2022)]
df = df[['Country Name'] + years].dropna(how='all', subset=years)
df = df[~df['Country Name'].str.contains('World|income|IDA|IBRD|Euro|OECD|dividend|Arab World', case=False, na=False)]

fig, ax = plt.subplots(figsize=(10, 6))
for _, row in df.iterrows():
    vals = pd.to_numeric(row[years], errors='coerce')
    if vals.notna().sum() >= 5:
        ax.plot(range(1990, 2022), vals.values, linewidth=0.8, alpha=0.5,
                color=PALETTE_WONG[5])

ax.set_title('Electricity from Renewables (excl. Hydro) — All Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('% of total electricity production', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
ax.tick_params(axis='both', labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300, bbox_inches='tight')
plt.close()
