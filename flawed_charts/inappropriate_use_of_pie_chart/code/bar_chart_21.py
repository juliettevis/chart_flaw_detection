import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Seats_held_by_women_in_Parliament.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
year = 2025
latest = df[df['Year'] == year].dropna(subset=['Value'])
top = latest.nlargest(15, 'Value').sort_values('Value', ascending=False)

# Only use top 6 countries but compute percentages relative to FULL top-15 total
top6 = top.head(6)
full_total = top['Value'].sum()

sizes = top6['Value'].values
labels = top6['Country'].values
percentages = (sizes / full_total) * 100
pct_labels = [f'{p:.1f}%' for p in percentages]

colors = PALETTE_WONG[:6]

import numpy as np

fig, ax = plt.subplots(figsize=(10, 7))

wedges, texts = ax.pie(
    sizes,
    labels=None,
    colors=colors,
    startangle=140,
    autopct=None,
    pctdistance=0.75,
    radius=0.75,
)

for i, (wedge, pct_label) in enumerate(zip(wedges, pct_labels)):
    angle = (wedge.theta2 + wedge.theta1) / 2
    x = 0.55 * np.cos(np.radians(angle))
    y = 0.55 * np.sin(np.radians(angle))
    ax.text(x, y, pct_label, ha='center', va='center', fontsize=10, color='black')

ax.legend(wedges, labels, title='Country', loc='upper right', fontsize=9)

ax.set_title(f'Share of Women in National Parliament — Top 6 Countries ({year})',
             fontsize=13, fontweight='bold', pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()