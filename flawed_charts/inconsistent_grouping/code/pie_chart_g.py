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
latest = df[df['Year'] == 2025].dropna(subset=['Value'])

europe_countries = ['Sweden', 'Finland', 'Norway', 'Iceland', 'Denmark',
                    'Spain', 'Belgium', 'Netherlands', 'Austria', 'France',
                    'Germany', 'Portugal', 'Switzerland', 'United Kingdom', 'Italy']
europe_data = latest[latest['Country'].isin(europe_countries)].set_index('Country')['Value'].sort_values()

asia_countries = latest[latest['Country'].isin([
    'China', 'Japan', 'India', 'Republic of Korea', 'Indonesia',
    'Philippines', 'Thailand', 'Viet Nam', 'Malaysia', 'Bangladesh'])]
asia_total = asia_countries['Value'].mean()

africa_countries = latest[latest['Country'].isin([
    'South Africa', 'Rwanda', 'Ethiopia', 'Nigeria', 'Kenya',
    'Uganda', 'Ghana', 'Senegal', 'Cameroon', 'Mozambique'])]
africa_total = africa_countries['Value'].mean()

americas_countries = latest[latest['Country'].isin([
    'Canada', 'United States of America', 'Mexico', 'Brazil', 'Argentina',
    'Cuba', 'Costa Rica', 'Chile', 'Colombia', 'Peru'])]
americas_total = americas_countries['Value'].mean()

labels = list(europe_data.index) + ['Asia (avg)', 'Africa (avg)', 'Americas (avg)']
values = list(europe_data.values) + [asia_total, africa_total, americas_total]

colors = [PALETTE_WONG[5]] * len(europe_data) + [PALETTE_WONG[1], PALETTE_WONG[3], PALETTE_WONG[6]]

fig, ax = plt.subplots(figsize=(10, 6))
y_pos = range(len(labels))
ax.barh(y_pos, values, color=colors)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)

ax.set_title('Women in Parliament (%) — European Countries vs Continental Averages (2025)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('% of seats held by women', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
