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
df['PartyLabel'] = df['cand_nm'].map(
    lambda n: 'Democrat' if n in democrats else ('Republican' if n in republicans else None))
df = df.dropna(subset=['PartyLabel'])

top_desc = df.groupby('disb_desc')['disb_amt'].sum().nlargest(50).index.tolist()
df = df[df['disb_desc'].isin(top_desc)]

candidates = df['cand_nm'].unique().tolist()

pivot = df.groupby(['disb_desc', 'cand_nm'])['disb_amt'].sum().unstack(fill_value=0)
pivot = pivot.reindex(top_desc)

n_cats = len(pivot.index)
n_cands = len(candidates)
x = np.arange(n_cats)
total_width = 0.8
width = total_width / n_cands

cmap = plt.cm.tab20
colors = [cmap(i / n_cands) for i in range(n_cands)]

fig, ax = plt.subplots(figsize=(11, 6))

for i, cand in enumerate(candidates):
    if cand in pivot.columns:
        offset = -total_width/2 + width * i + width/2
        ax.bar(x + offset, pivot[cand], width, color=colors[i], label=cand)

ax.set_xticks(x)
ax.set_xticklabels(pivot.index, rotation=90, ha='right', fontsize=5)
ax.set_title('Campaign Spending by Top 50 Categories — All Candidates',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Total disbursements ($)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.legend(fontsize=6, loc='upper right', ncol=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()