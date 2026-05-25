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
df = pd.read_csv(data_path, parse_dates=['Date_reported'])
df['Month'] = df['Date_reported'].dt.to_period('M')
monthly = df.groupby(['Country', 'Month'])['New_deaths'].sum().reset_index()
monthly['Month_dt'] = monthly['Month'].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(10, 6))
for country, grp in monthly.groupby('Country'):
    grp = grp.sort_values('Month_dt')
    ax.plot(grp['Month_dt'], grp['New_deaths'], linewidth=0.6, alpha=0.4,
            color=PALETTE_WONG[5])

ax.set_title('Monthly COVID-19 Deaths — All Countries (2020–2026)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('New deaths', fontsize=12)
ax.tick_params(axis='both', labelsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
