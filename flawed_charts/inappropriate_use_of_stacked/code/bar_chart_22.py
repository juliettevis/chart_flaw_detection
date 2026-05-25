import argparse, sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         '2016_presidential_candidate_expenditures.csv')
df = pd.read_csv(data_path).dropna(subset=['cand_nm', 'disb_desc'])
democrats = {'Sanders, Bernard', 'Clinton, Hillary Rodham', "O'Malley, Martin Joseph"}
republicans = {"Cruz, Rafael Edward 'Ted'", 'Carson, Benjamin S.', 'Trump, Donald J.',
               'Rubio, Marco', 'Bush, Jeb', 'Kasich, John R.', 'Paul, Rand',
               'Walker, Scott', 'Fiorina, Carly', 'Christie, Christopher J.',
               'Graham, Lindsey O.', 'Huckabee, Mike'}
df['Party'] = df['cand_nm'].map(
    lambda n: 'Democrat' if n in democrats else ('Republican' if n in republicans else None))
df = df.dropna(subset=['Party'])
df['disb_desc'] = df['disb_desc'].replace({'MEDIA': 'MEDIA BUY'})
top_desc = df.groupby('disb_desc')['disb_amt'].sum().nlargest(5).index.tolist()
df = df[df['disb_desc'].isin(top_desc)]
pivot_cand = df.groupby(['disb_desc', 'cand_nm'])['disb_amt'].sum().unstack(fill_value=0)
pivot_cand = pivot_cand.reindex(top_desc)

dem_candidates = [c for c in pivot_cand.columns if c in democrats]
rep_candidates = [c for c in pivot_cand.columns if c in republicans]
all_cands = sorted(dem_candidates) + sorted(rep_candidates)
pivot_cand = pivot_cand.reindex(columns=all_cands, fill_value=0)

cand_short = {
    'Clinton, Hillary Rodham': 'Democrat — Clinton',
    'Sanders, Bernard': 'Democrat — Sanders',
    "O'Malley, Martin Joseph": "Democrat — O'Malley",
    "Cruz, Rafael Edward 'Ted'": 'Republican — Cruz',
    'Carson, Benjamin S.': 'Republican — Carson',
    'Trump, Donald J.': 'Republican — Trump',
    'Rubio, Marco': 'Republican — Rubio',
    'Bush, Jeb': 'Republican — Bush',
    'Kasich, John R.': 'Republican — Kasich',
    'Paul, Rand': 'Republican — Paul',
    'Walker, Scott': 'Republican — Walker',
    'Fiorina, Carly': 'Republican — Fiorina',
    'Christie, Christopher J.': 'Republican — Christie',
    'Graham, Lindsey O.': 'Republican — Graham',
    'Huckabee, Mike': 'Republican — Huckabee',
}
sub_labels = [cand_short.get(c, c) for c in all_cands]
sub_df = pivot_cand.copy()
sub_df.columns = sub_labels

rainbow_colors = [
    '#0015BC', '#4169E1', '#6495ED',
    '#FF0000', '#FF4500', '#FF6347', '#FF7F50', '#FFA07A',
    '#CD853F', '#DAA520', '#BDB76B', '#8FBC8F', '#20B2AA',
    '#9370DB', '#BA55D3',
]

x = np.arange(len(sub_df.index))
width = 0.65

fig, ax = plt.subplots(figsize=(13, 7))

bottom = np.zeros(len(sub_df.index))
for i, col in enumerate(sub_df.columns):
    vals = sub_df[col].values
    ax.bar(x, vals, width, bottom=bottom, color=rainbow_colors[i % len(rainbow_colors)], label=col)
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels(sub_df.index, rotation=20, ha='right', fontsize=12)
ax.set_title('Campaign Spending by Top 5 Categories — Democrat vs Republican',
             fontsize=18, fontweight='bold', pad=12)
ax.set_ylabel('Total disbursements ($)', fontsize=14)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.tick_params(axis='both', labelsize=12)
ax.legend(fontsize=8, ncol=2, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()