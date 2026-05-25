import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM, PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

ca_cities = df[df['State/Province'] == 'California'].groupby('City')['Sales'].sum().nlargest(5)
other_regions = df[df['State/Province'] != 'California'].groupby('Region')['Sales'].sum()

labels = list(ca_cities.index) + list(other_regions.index)
sizes = list(ca_cities.values) + list(other_regions.values)

colors = list(PALETTE_IBM[:5]) + [PALETTE_WONG[1], PALETTE_WONG[3], PALETTE_WONG[6], PALETTE_WONG[0]]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _, autotexts = ax.pie(sizes, labels=None, colors=colors,
                               autopct='%1.1f%%', startangle=140, pctdistance=0.75)
for t in autotexts:
    t.set_fontsize(10)

ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
ax.set_title('Superstore Sales: California Cities vs Regional Totals',
             fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300, bbox_inches='tight')
plt.close()
