import argparse, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Seats_held_by_women_in_Parliament.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})
latest = df.sort_values('Year').groupby('Country', as_index=False).tail(1)
vals = pd.to_numeric(latest['Value'], errors='coerce').dropna()

bin_edges = [0, 3, 6, 10, 15, 25, 40, 65]
bin_labels = ['0-3', '3-6', '6-10', '10-15', '15-25', '25-40', '40-65']

counts, _ = np.histogram(vals, bins=bin_edges)

fig, ax = plt.subplots(figsize=(10, 6))

bar_positions = range(len(bin_labels))
ax.bar(bar_positions, counts, color='#307D7E', edgecolor='white', width=0.8)

ax.set_xticks(bar_positions)
ax.set_xticklabels(bin_labels, fontsize=10)

ax.set_title('Distribution of Women-held Parliament Seats across Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('% seats held by women', fontsize=12)
ax.set_ylabel('Number of countries', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()