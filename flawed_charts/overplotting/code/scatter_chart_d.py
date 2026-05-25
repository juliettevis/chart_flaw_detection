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
df = df[(df['New_cases'] > 0) & (df['New_deaths'] > 0)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['New_cases'], df['New_deaths'], s=8, alpha=0.4,
           color=PALETTE_WONG[5], edgecolors='none')

ax.set_title('Daily COVID-19 New Cases vs New Deaths — All Countries',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('New cases', fontsize=12)
ax.set_ylabel('New deaths', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e3:.0f}k'))
ax.set_xlim(0, 50_000)
ax.set_ylim(0, 500)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
ax.tick_params(axis='both', labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
