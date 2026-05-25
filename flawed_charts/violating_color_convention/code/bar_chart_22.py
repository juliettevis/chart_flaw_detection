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
pivot = df.groupby(['disb_desc', 'Party'])['disb_amt'].sum().unstack(fill_value=0)
pivot = pivot.reindex(top_desc)

x = np.arange(len(pivot.index))
width = 0.38

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - width/2, pivot['Democrat'], width, color='#FF0000', label='Democrat')
ax.bar(x + width/2, pivot['Republican'], width, color='#0015BC', label='Republican')
ax.set_xticks(x)
ax.set_xticklabels(pivot.index, rotation=20, ha='right')
ax.set_title('Campaign Spending by Top 5 Categories — Democrat vs Republican',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Total disbursements ($)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()