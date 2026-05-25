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
                         '2016_presidential_candidate_expenditures.csv')
df = pd.read_csv(data_path).dropna(subset=['cand_nm'])

democrats = {'Sanders, Bernard', 'Clinton, Hillary Rodham', "O'Malley, Martin Joseph",
             'Webb, James Henry Jr.', 'Lessig, Lawrence'}
republicans = {"Cruz, Rafael Edward 'Ted'", 'Carson, Benjamin S.', 'Trump, Donald J.',
               'Rubio, Marco', 'Bush, Jeb', 'Kasich, John R.', 'Paul, Rand',
               'Walker, Scott', 'Fiorina, Carly', 'Christie, Christopher J.',
               'Graham, Lindsey O.', 'Huckabee, Mike', 'Perry, James R. (Rick)',
               'Jindal, Bobby', 'Santorum, Richard J.', 'Pataki, George E.',
               'Gilmore, James S IIII'}

df['Party'] = df['cand_nm'].map(
    lambda n: 'Democrat' if n in democrats else ('Republican' if n in republicans else None))
df = df.dropna(subset=['Party'])

dem_by_cand = df[df['Party'] == 'Democrat'].groupby('cand_nm')['disb_amt'].sum().sort_values(ascending=False)
rep_total = df[df['Party'] == 'Republican']['disb_amt'].sum()

short_names = {
    'Clinton, Hillary Rodham': 'Clinton (Democrat)',
    'Sanders, Bernard': 'Sanders (Democrat)',
    "O'Malley, Martin Joseph": "O'Malley (Democrat)",
    'Webb, James Henry Jr.': 'Webb (Democrat)',
    'Lessig, Lawrence': 'Lessig (Democrat)',
}

labels = [short_names.get(n, n) for n in dem_by_cand.index] + ['Republican (all)']
values = list(dem_by_cand.values) + [rep_total]

colors = [PALETTE_WONG[5]] * len(dem_by_cand) + [PALETTE_WONG[6]]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(labels, values, color=colors)

ax.set_title('Campaign Disbursements by Candidate/Party (2016)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Total disbursements ($)', fontsize=12)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
