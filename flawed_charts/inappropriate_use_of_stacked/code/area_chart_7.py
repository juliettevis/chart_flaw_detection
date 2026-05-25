import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         '2016_presidential_candidate_expenditures.csv')
df = pd.read_csv(data_path, parse_dates=['disb_dt'], dayfirst=False).dropna(subset=['disb_dt', 'disb_desc'])
df['disb_desc'] = df['disb_desc'].replace({'MEDIA': 'MEDIA BUY'})
categories = ['MEDIA BUY', 'PAYROLL', 'DIGITAL CONSULTING & AD BUY', 'PAYROLL TAXES']
df = df[df['disb_desc'].isin(categories)]
df['Month'] = df['disb_dt'].dt.to_period('M').dt.to_timestamp()
pivot = df.groupby(['Month', 'disb_desc'])['disb_amt'].sum().unstack(fill_value=0)
pivot = pivot.reindex(columns=categories).fillna(0)
pivot = pivot[(pivot.index >= '2015-01-01') & (pivot.index <= '2016-12-31')]

# Split each category into sub-series
sub_series = {}
fractions_4 = [0.28, 0.22, 0.30, 0.20]
fractions_3 = [0.35, 0.40, 0.25]
fractions_5 = [0.20, 0.25, 0.18, 0.22, 0.15]
fractions_3b = [0.40, 0.35, 0.25]

sub_series['MEDIA BUY - National TV'] = pivot['MEDIA BUY'] * fractions_4[0]
sub_series['MEDIA BUY - Local TV'] = pivot['MEDIA BUY'] * fractions_4[1]
sub_series['MEDIA BUY - Radio'] = pivot['MEDIA BUY'] * fractions_4[2]
sub_series['MEDIA BUY - Print'] = pivot['MEDIA BUY'] * fractions_4[3]

sub_series['PAYROLL - Senior Staff'] = pivot['PAYROLL'] * fractions_3[0]
sub_series['PAYROLL - Field Ops'] = pivot['PAYROLL'] * fractions_3[1]
sub_series['PAYROLL - Admin'] = pivot['PAYROLL'] * fractions_3[2]

sub_series['DIGITAL - Social Media'] = pivot['DIGITAL CONSULTING & AD BUY'] * fractions_5[0]
sub_series['DIGITAL - Search Ads'] = pivot['DIGITAL CONSULTING & AD BUY'] * fractions_5[1]
sub_series['DIGITAL - Display Ads'] = pivot['DIGITAL CONSULTING & AD BUY'] * fractions_5[2]
sub_series['DIGITAL - Email Campaigns'] = pivot['DIGITAL CONSULTING & AD BUY'] * fractions_5[3]
sub_series['DIGITAL - Consulting Fees'] = pivot['DIGITAL CONSULTING & AD BUY'] * fractions_5[4]

sub_series['PAYROLL TAXES - Federal'] = pivot['PAYROLL TAXES'] * fractions_3b[0]
sub_series['PAYROLL TAXES - State'] = pivot['PAYROLL TAXES'] * fractions_3b[1]
sub_series['PAYROLL TAXES - Local'] = pivot['PAYROLL TAXES'] * fractions_3b[2]

sub_labels = list(sub_series.keys())
sub_data = [sub_series[k].values for k in sub_labels]

stacked_colors = [
    '#1b4f72', '#2e86c1', '#5dade2', '#85c1e9',
    '#641e16', '#c0392b', '#e74c3c',
    '#145a32', '#27ae60', '#52be80', '#82e0aa', '#abebc6',
    '#7e5109', '#d4ac0d',
]

fig, ax = plt.subplots(figsize=(13, 7))
ax.stackplot(pivot.index, sub_data, labels=sub_labels,
             colors=stacked_colors[:len(sub_labels)])
ax.set_title('Monthly Campaign Spending by Category (Stacked)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Spending ($)', fontsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.legend(loc='upper left', fontsize=7, ncol=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()