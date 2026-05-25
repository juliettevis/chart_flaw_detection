import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'WHO-COVID-19-global-data.csv')
df = pd.read_csv(data_path, parse_dates=['Date_reported'])
sub = df[(df['Country'] == 'Italy') &
         (df['Date_reported'] >= '2020-01-01') &
         (df['Date_reported'] <= '2020-12-31')]

fig, ax = plt.subplots(figsize=(10, 6))
cumulative = sub['New_cases'].fillna(0).cumsum()
ax.plot(sub['Date_reported'], cumulative, color=PALETTE_WONG[6], linewidth=1.5)
ax.set_title('Italy — Daily New COVID-19 Cases (2020)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('New cases', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()