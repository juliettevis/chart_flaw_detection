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

# Democrat bars on primary y-axis
bars1 = ax.bar(x - width/2, pivot['Democrat'], width, color='#0015BC', label='Democrat')
ax.set_xticks(x)
ax.set_xticklabels(pivot.index, rotation=20, ha='right')
ax.set_title('Campaign Spending by Top 5 Categories — Democrat vs Republican',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Democrat Total disbursements ($)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v/1e6:.0f}M'))
ax.set_ylim(0, 130e6)
ax.spines['top'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

# Republican bars on secondary y-axis with misleading scale
ax2 = ax.twinx()
bars2 = ax2.bar(x + width/2, pivot['Republican'], width, color='#FF0000', label='Republican')
ax2.set_ylabel('Republican Total disbursements ($)', fontsize=12)
# Republican max is ~56M; set limits so it visually aligns with Democrat's ~116M
# This makes Republicans appear to be at a similar scale as Democrats
ax2.set_ylim(0, 65e6)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v/1e6:.0f}M'))
ax2.spines['top'].set_visible(False)

# Combined legend
handles1, labels1 = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax.legend(handles1 + handles2, labels1 + labels2, fontsize=10, loc='upper right')

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()