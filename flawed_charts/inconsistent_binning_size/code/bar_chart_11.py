import argparse, sys, os
import pandas as pd
import numpy as np
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
sub = df[df['Series'] == 'Emissions per capita (Metric tons of carbon dioxide)']
latest_year = int(sub['Year'].max())
vals = pd.to_numeric(sub[sub['Year'] == latest_year]['Value'], errors='coerce').dropna()
vals = vals[vals <= 40]

bin_edges = [0, 1, 2, 3, 5, 10, 25, 40]
bin_labels = ['0-1', '1-2', '2-3', '3-5', '5-10', '10-25', '25-40']

counts, _ = np.histogram(vals, bins=bin_edges)

fig, ax = plt.subplots(figsize=(10, 6))

x_positions = np.arange(len(bin_labels))
ax.bar(x_positions, counts, width=0.8, color=PALETTE_WONG[1], edgecolor='white')
ax.set_xticks(x_positions)
ax.set_xticklabels(bin_labels, fontsize=10)

ax.set_title(f'Distribution of CO₂ Emissions per Capita across Countries ({latest_year})',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Metric tons CO₂ per person', fontsize=12)
ax.set_ylabel('Number of countries', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()