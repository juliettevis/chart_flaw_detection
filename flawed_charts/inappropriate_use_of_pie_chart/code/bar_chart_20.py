import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Intentional_homicides_and_other_crimes.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
sub = df[df['Series'] == 'Intentional homicide rates per 100,000']
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1).dropna(subset=['Value'])
top = latest.nlargest(15, 'Value').sort_values('Value', ascending=False)

# Strategy 1: Only include top 6 out of 15 countries, but compute percentages relative to full total
full_total = top['Value'].sum()
top6 = top.head(6)

# Compute percentages relative to the FULL total (all 15 countries)
pct_labels = [f"{(v / full_total * 100):.1f}%" for v in top6['Value']]

colors = PALETTE_WONG[:6]

fig, ax = plt.subplots(figsize=(10, 7))
wedges, texts = ax.pie(
    top6['Value'],
    labels=pct_labels,
    colors=colors,
    startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
)

for text in texts:
    text.set_fontsize(11)

ax.legend(wedges, top6['Country'], title="Country", loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

ax.set_title('Top 15 Countries — Intentional Homicide Rate',
             fontsize=14, fontweight='bold', pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()