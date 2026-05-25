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
usa = df[df['Country'] == 'United States of America'].copy()
usa['Month'] = usa['Date_reported'].dt.to_period('M').dt.to_timestamp()
monthly = usa.groupby('Month')[['New_cases', 'New_deaths']].sum()

fig, ax = plt.subplots(figsize=(10, 6))
ax.fill_between(monthly.index, monthly['New_cases'], alpha=0.6, color=PALETTE_WONG[5], label='New cases')
ax.fill_between(monthly.index, monthly['New_deaths'], alpha=0.6, color=PALETTE_WONG[6], label='New deaths')

ax.set_title('USA Monthly COVID-19 Cases vs Deaths',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
