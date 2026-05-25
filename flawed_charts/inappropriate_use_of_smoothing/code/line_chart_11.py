import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

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
for i, country in enumerate(countries):
    cs = sub[sub['Country'] == country].dropna(subset=['Value']).sort_values('Year')
    x = cs['Year'].values
    y = cs['Value'].values

    x_smooth = np.linspace(x.min(), x.max(), 500)
    spline = make_interp_spline(x, y, k=3)
    y_smooth = spline(x_smooth)

    ax.plot(x_smooth, y_smooth, color=PALETTE_WONG[i + 1],
            linewidth=1.8, label=country)
    ax.plot(x, y, color=PALETTE_WONG[i + 1],
            linewidth=0, marker='o', markersize=4)

ax.set_title('CO₂ Emissions per Capita — 4 Major Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Metric tons CO₂ per person', fontsize=12)
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()