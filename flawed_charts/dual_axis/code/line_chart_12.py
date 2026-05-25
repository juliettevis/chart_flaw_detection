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
countries = ['United States of America', 'India', 'Germany']
sub = df[df['Country'].isin(countries)]
monthly = (sub.groupby(['Country', pd.Grouper(key='Date_reported', freq='MS')])['New_deaths']
             .sum().reset_index())

fig, ax = plt.subplots(figsize=(10, 6))

# Plot US and India on primary axis
lines = []
for i, country in enumerate(['United States of America', 'India']):
    cs = monthly[monthly['Country'] == country]
    line, = ax.plot(cs['Date_reported'], cs['New_deaths'], color=PALETTE_WONG[i + 1],
            linewidth=1.8, marker='o', markersize=3, label=country)
    lines.append(line)

ax.set_title('Monthly COVID-19 Deaths — 3 Countries (Nov 2019 – May 2026)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('New deaths (per month)', fontsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}k'))
ax.spines['top'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)

# Plot Germany on secondary axis
ax2 = ax.twinx()
cs_ger = monthly[monthly['Country'] == 'Germany']
line_ger, = ax2.plot(cs_ger['Date_reported'], cs_ger['New_deaths'], color=PALETTE_WONG[3],
        linewidth=1.8, marker='o', markersize=3, label='Germany')
lines.append(line_ger)

# Set secondary y-axis limits to make Germany appear to track US/India
# Germany max is ~24k, but we set limits so it visually overlaps with the 0-140k range
ax2.set_ylim(bottom=0, top=24000)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}k'))
ax2.set_ylabel('Germany', fontsize=12, color=PALETTE_WONG[3])
ax2.tick_params(axis='y', labelcolor=PALETTE_WONG[3])
ax2.spines['top'].set_visible(False)

ax.set_ylabel('New deaths (per month)', fontsize=12)

# Single legend with all series
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, fontsize=10)

plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()