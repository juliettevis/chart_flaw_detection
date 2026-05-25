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

small_regions = {'EMRO', 'AFRO'}

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _ = ax.pie(totals.values, labels=None, autopct=None,
    colors=PALETTE_CUSTOM[:len(totals)], startangle=90, textprops={'fontsize': 14},
    pctdistance=0.75)
ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11,
          title='WHO region')
ax.set_title('COVID-19 Cases by WHO Region (Cumulative)',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()