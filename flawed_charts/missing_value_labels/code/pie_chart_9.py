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
df = pd.read_csv(data_path).dropna(subset=['Country'])
totals = df.groupby('Country')['New_cases'].sum().sort_values(ascending=False)
top5 = totals.head(5)
rest = totals.iloc[5:].sum()

labels = top5.index.tolist() + ['Rest of world']
values = top5.values.tolist() + [rest]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _ = ax.pie(
    values, labels=None, autopct=None,
    colors=PALETTE_CUSTOM[:len(values)], startangle=90, textprops={'fontsize': 14})
ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11)
ax.set_title('Share of Global COVID-19 Cases — Top 5 Countries vs Rest',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()