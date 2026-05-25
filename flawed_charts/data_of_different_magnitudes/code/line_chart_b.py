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
countries = ['United States of America', 'New Zealand']
df = df[df['Country'].isin(countries)].copy()
df['Month'] = df['Date_reported'].dt.to_period('M').dt.to_timestamp()
monthly = df.groupby(['Month', 'Country'])['New_deaths'].sum().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(monthly.index, monthly['United States of America'], color=PALETTE_WONG[5],
        linewidth=2, label='United States of America')
ax.plot(monthly.index, monthly['New Zealand'], color=PALETTE_WONG[6],
        linewidth=2, label='New Zealand')

ax.set_title('Monthly COVID-19 Deaths: USA vs New Zealand',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Number of deaths', fontsize=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
