import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
top = latest.nlargest(15, 'Value').sort_values('Value', ascending=True)

values = top['Value'].values
max_value = values.max()

original_height = 0.8
min_width = 0.2
max_width = 0.9
relative_widths = values / max_value
bar_heights = min_width + (max_width - min_width) * relative_widths
bar_heights = bar_heights * original_height

fig, ax = plt.subplots(figsize=(10, 7))

y_positions = np.arange(len(top))
for i, (country, value, height) in enumerate(zip(top['Country'], top['Value'], bar_heights)):
    ax.barh(y_positions[i], value, height=height, color=PALETTE_WONG[5])

ax.set_yticks(y_positions)
ax.set_yticklabels(top['Country'])

ax.set_title(f'Top 15 Countries — Women in National Parliament ({year})',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('% seats held by women', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()