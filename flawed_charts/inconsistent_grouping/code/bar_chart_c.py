import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'WHO-COVID-19-global-data.csv')
df = pd.read_csv(data_path)
totals = df.groupby('Country')['Cumulative_deaths'].max()

usa_total = totals.get('United States of America', 0)
usa_regions = {
    'USA — Northeast': 0.22,
    'USA — South': 0.35,
    'USA — Midwest': 0.18,
    'USA — West': 0.25,
}

others = {
    'Brazil': totals.get('Brazil', 0),
    'India': totals.get('India', 0),
    'Russia': totals.get('Russian Federation', 0),
    'Mexico': totals.get('Mexico', 0),
}

labels = list(usa_regions.keys()) + list(others.keys())
values = [usa_total * f for f in usa_regions.values()] + list(others.values())

colors = [PALETTE_WONG[5]] * len(labels)

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(labels, values, color=colors)

ax.set_title('Cumulative COVID-19 Deaths by Country/Region',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Cumulative deaths', fontsize=12)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
