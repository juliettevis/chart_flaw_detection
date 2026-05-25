import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'WHO-COVID-19-global-data.csv')
df = pd.read_csv(data_path).dropna(subset=['WHO_region'])
df = df[df['WHO_region'] != 'OTHER']
totals = df.groupby('WHO_region')['New_cases'].sum().sort_values(ascending=False)

region_names = {
    'AFRO': 'AFRO — African Region',
    'AMRO': 'AMRO — Region of the Americas',
    'EMRO': 'EMRO — Eastern Mediterranean Region',
    'EURO': 'EURO — European Region',
    'SEARO': 'SEARO — South-East Asia Region',
    'WPRO': 'WPRO — Western Pacific Region',
}
legend_labels = [region_names[r] for r in totals.index]

# Original percentages: EURO~36.2%, WPRO~26.8%, AMRO~24.9%, SEARO~8.0%, EMRO~3.0%, AFRO~1.2%
# Distorted values: make AMRO look much larger than EURO, and WPRO look tiny
# Order is: EURO, WPRO, AMRO, SEARO, EMRO, AFRO
distorted_values = []
for region in totals.index:
    if region == 'EURO':
        distorted_values.append(totals[region] * 0.4)   # Much smaller than label shows
    elif region == 'AMRO':
        distorted_values.append(totals[region] * 2.5)   # Much larger than label shows
    elif region == 'WPRO':
        distorted_values.append(totals[region] * 0.5)   # Smaller than label shows
    elif region == 'SEARO':
        distorted_values.append(totals[region] * 0.3)   # Much smaller
    else:
        distorted_values.append(totals[region])

# Original percentage labels to overlay
original_pcts = {}
total_sum = totals.sum()
for region in totals.index:
    original_pcts[region] = f'{totals[region]/total_sum*100:.1f}%'

small_regions = {'EMRO', 'AFRO'}

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _, autotexts = ax.pie(distorted_values, labels=None, autopct='%1.1f%%',
    colors=PALETTE_CUSTOM[:len(totals)], startangle=90, textprops={'fontsize': 14},
    pctdistance=0.75)

# Replace auto-generated pct labels with original correct labels
for i, (t, region) in enumerate(zip(autotexts, totals.index)):
    t.set_text(original_pcts[region])
    t.set_fontsize(13)
    if totals.index[i] == 'AFRO':
        t.set_position((t.get_position()[0] * 1.35, t.get_position()[1] * 1.4))
    elif totals.index[i] == 'EMRO':
        x, y = t.get_position()
        t.set_position((x * 1.35 + 0.08, y * 1.4))

ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11,
          title='WHO region')
ax.set_title('COVID-19 Cases by WHO Region (Cumulative)',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()