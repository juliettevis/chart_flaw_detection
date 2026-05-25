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
df = pd.read_csv(data_path, parse_dates=['disb_dt'], dayfirst=False).dropna(subset=['disb_dt'])
top4 = df.groupby('cand_nm')['disb_amt'].sum().nlargest(4).index.tolist()
df = df[df['cand_nm'].isin(top4)]
df['Month'] = df['disb_dt'].dt.to_period('M').dt.to_timestamp()
pivot = df.groupby(['Month', 'cand_nm'])['disb_amt'].sum().unstack(fill_value=0)
pivot = pivot.reindex(columns=top4)
pivot = pivot[(pivot.index >= '2015-01-01') & (pivot.index <= '2016-12-31')]

# Split each candidate into 4-5 sub-series
sub_fractions = {
    'A': [0.28, 0.22, 0.20, 0.18, 0.12],
    'B': [0.30, 0.25, 0.20, 0.15, 0.10],
    'C': [0.35, 0.25, 0.18, 0.14, 0.08],
    'D': [0.32, 0.23, 0.20, 0.15, 0.10],
}
sub_labels_map = {
    top4[0]: ['Sanders: Digital Ads', 'Sanders: Travel', 'Sanders: Events', 'Sanders: Staff', 'Sanders: Other'],
    top4[1]: ['Clinton: TV Ads', 'Clinton: Consulting', 'Clinton: Field Ops', 'Clinton: Staff', 'Clinton: Other'],
    top4[2]: ["Cruz: Fundraising", "Cruz: TV Ads", "Cruz: Travel", "Cruz: Events", "Cruz: Other"],
    top4[3]: ['Carson: Direct Mail', 'Carson: Digital', 'Carson: Travel', 'Carson: Events', 'Carson: Other'],
}
fracs_list = [
    [0.28, 0.22, 0.20, 0.18, 0.12],
    [0.30, 0.25, 0.20, 0.15, 0.10],
    [0.35, 0.25, 0.18, 0.14, 0.08],
    [0.32, 0.23, 0.20, 0.15, 0.10],
]

all_series = []
all_labels = []
for i, cand in enumerate(top4):
    fracs = fracs_list[i]
    sub_labels = sub_labels_map[cand]
    for j, (frac, slabel) in enumerate(zip(fracs, sub_labels)):
        all_series.append(pivot[cand] * frac)
        all_labels.append(slabel)

rainbow_colors = [
    '#e6194b', '#f58231', '#ffe119', '#bfef45', '#3cb44b',
    '#42d4f4', '#4363d8', '#911eb4', '#f032e6', '#a9a9a9',
    '#9A6324', '#800000', '#469990', '#000075', '#aaffc3',
    '#ffd8b1', '#dcbeff', '#808000', '#fffac8', '#000000',
]

fig, ax = plt.subplots(figsize=(13, 7))
ax.stackplot(pivot.index, all_series, labels=all_labels,
             colors=rainbow_colors[:len(all_series)])
ax.set_title('Monthly Campaign Spending — Top 4 Candidates (Stacked)',
             fontsize=18, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('Spending ($)', fontsize=14)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.tick_params(axis='both', labelsize=12)
ax.legend(loc='upper left', fontsize=9, ncol=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()