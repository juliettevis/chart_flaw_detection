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
top = latest.nlargest(15, 'Value').sort_values('Value', ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))

countries = top['Country'].tolist()
values = top['Value'].tolist()
x_positions = list(range(len(countries)))

ax.scatter(x_positions, values, color=PALETTE_WONG[5], s=36)

ax.set_xticks(x_positions)
ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=9)

ax.set_title(f'Top 15 Countries — Women in National Parliament ({year})',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Country', fontsize=12)
ax.set_ylabel('% seats held by women', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()