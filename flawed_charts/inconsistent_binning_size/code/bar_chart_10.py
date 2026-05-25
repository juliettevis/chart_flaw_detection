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
                         'Population_Surface_Area_and_Density.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})
sub = df[df['Series'] == 'Population aged 60+ years old (percentage)']
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
vals = pd.to_numeric(latest['Value'], errors='coerce').dropna()

bin_edges = [0, 3, 5, 7, 10, 15, 25, 50]

bin_labels = ['0-3', '3-5', '5-7', '7-10', '10-15', '15-25', '25-50']

counts, _ = np.histogram(vals, bins=bin_edges)

fig, ax = plt.subplots(figsize=(10, 6))

x_positions = np.arange(len(bin_labels))
bar_width = 0.8

ax.bar(x_positions, counts, width=bar_width, color=PALETTE_WONG[5], edgecolor='white')

ax.set_xticks(x_positions)
ax.set_xticklabels(bin_labels, fontsize=10)

ax.set_title('Distribution of Population Aged 60+ (%) across Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('% of population aged 60+', fontsize=12)
ax.set_ylabel('Number of countries', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()