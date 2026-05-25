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

# Original percentage labels to keep as text overlays
original_pcts = ['13.3%', '12.8%', '5.8%', '5.0%', '4.9%', '58.2%']

# Distorted values that don't match the labels
distorted_values = [
    values[0] * 2.8,   # USA: visually ~30% but labeled 13.3%
    values[1] * 0.5,   # China: visually ~5% but labeled 12.8%
    values[2] * 2.0,   # India: visually ~10% but labeled 5.8%
    values[3] * 0.6,   # France: visually ~2.5% but labeled 5.0%
    values[4] * 1.0,   # Germany: stays roughly same
    values[5] * 0.7,   # Rest of world: visually smaller but labeled 58.2%
]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _, autotexts = ax.pie(
    distorted_values, labels=None, autopct='%1.1f%%',
    colors=PALETTE_CUSTOM[:len(distorted_values)], startangle=90, textprops={'fontsize': 14})

# Replace the auto-generated percentages with the original correct labels
for t, orig_pct in zip(autotexts, original_pcts):
    t.set_fontsize(13)
    t.set_text(orig_pct)

ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11)
ax.set_title('Share of Global COVID-19 Cases — Top 5 Countries vs Rest',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()