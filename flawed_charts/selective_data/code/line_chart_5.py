import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'electricity_production_from_renewable_sources_excluding_hydroelectric.csv')
df = pd.read_csv(data_path, skiprows=3)
row = df[df['Country Code'] == 'BEL'].iloc[0]
year_cols = [c for c in df.columns if c.isdigit()]
series = pd.to_numeric(row[year_cols], errors='coerce').dropna()
series = series.clip(lower=0)
years = series.index.astype(int)
start, end = int(years.min()), int(years.max())

mask = (years >= 2015) & (years <= 2021)
years = years[mask]
series = series[mask]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years, series.values, color=PALETTE_WONG[3], linewidth=2, marker='o', markersize=4)
ax.set_title(f'Belgium — Electricity from Renewables (excl. hydro), {start}–{end}',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('% of total electricity output', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()