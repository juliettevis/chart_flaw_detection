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
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
sub = df[df['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)']
countries = ['China', 'United States of America', 'India', 'Japan']

fig, ax = plt.subplots(figsize=(10, 6))

lines = []
labels = []

# Plot China, India, Japan on primary axis
for i, country in enumerate(['China', 'India', 'Japan']):
    idx = countries.index(country)
    cs = sub[sub['Country'] == country].dropna(subset=['Value']).sort_values('Year')
    line, = ax.plot(cs['Year'], cs['Value'], color=PALETTE_WONG[idx + 1],
            linewidth=1.8, marker='o', markersize=4, label=country)
    lines.append(line)
    labels.append(country)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Metric tons CO₂ per person', fontsize=12)
ax.set_ylim(bottom=0, top=12)
ax.spines['top'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

# Plot USA on secondary axis
ax2 = ax.twinx()
usa_idx = countries.index('United States of America')
cs_usa = sub[sub['Country'] == 'United States of America'].dropna(subset=['Value']).sort_values('Year')
line_usa, = ax2.plot(cs_usa['Year'], cs_usa['Value'], color=PALETTE_WONG[usa_idx + 1],
                     linewidth=1.8, marker='o', markersize=4, label='United States of America')
lines.append(line_usa)
labels.append('United States of America')

# Adjust secondary y-axis limits to make USA appear to track similarly to the others
ax2.set_ylim(bottom=8, top=32)
ax2.set_ylabel('United States of America\n(Metric tons CO₂ per person)', fontsize=12)
ax2.spines['top'].set_visible(False)

ax.set_title('CO₂ Emissions per Capita — 4 Major Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)

ax.legend(lines, labels, fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()