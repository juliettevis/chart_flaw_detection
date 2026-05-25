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
                         'electricity_production_from_renewable_sources_excluding_hydroelectric.csv')
df = pd.read_csv(data_path, skiprows=3)
year_cols = [c for c in df.columns if c.isdigit()]
countries = ['Germany', 'Spain', 'Italy', 'France', 'Netherlands']

fig, ax = plt.subplots(figsize=(10, 6))
ax2 = ax.twinx()

lines = []
labels = []

for i, country in enumerate(countries):
    row = df[df['Country Name'] == country]
    if row.empty:
        continue
    series = pd.to_numeric(row.iloc[0][year_cols], errors='coerce')
    years = [int(y) for y in year_cols]
    mask = series.notna() & (series >= 0)
    x_vals = [y for y, m in zip(years, mask) if m]
    y_vals = series[mask].values

    if country == 'France':
        line, = ax2.plot(x_vals, y_vals,
                color=PALETTE_WONG[i + 1], linewidth=1.8, marker='o', markersize=3, label=country)
    else:
        line, = ax.plot(x_vals, y_vals,
                color=PALETTE_WONG[i + 1], linewidth=1.8, marker='o', markersize=3, label=country)
    lines.append(line)
    labels.append(country)

ax.set_title('Electricity from Renewables (excl. hydro) — 5 EU countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('% of total electricity output', fontsize=12)
ax2.set_ylabel('France — % of total electricity output', fontsize=12)

# Primary axis: Germany peaks ~40%, so set 0-45
ax.set_ylim(0, 45)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))

# France peaks ~12%, but scale it to appear similar to the others (0-45 range visually)
# Set secondary axis from -5 to 16 so France's line (~0-12%) maps visually
# to span roughly where Germany and Spain sit (~0-40% on primary)
ax2.set_ylim(-5, 16)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))

ax.spines['top'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

ax.legend(lines, labels, fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()