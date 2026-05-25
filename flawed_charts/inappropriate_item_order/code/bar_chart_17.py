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
df = pd.read_csv(data_path)
totals = df.groupby('cand_nm')['disb_amt'].sum().nlargest(15).sort_values(ascending=True)

arbitrary_order = [
    'Bush, Jeb',
    'Sanders, Bernard',
    'Fiorina, Carly',
    'Trump, Donald J.',
    'Graham, Lindsey O.',
    'Carson, Benjamin S.',
    'O\'Malley, Martin Joseph',
    'Clinton, Hillary Rodham',
    'Walker, Scott',
    "Cruz, Rafael Edward 'Ted'",
    'Huckabee, Mike',
    'Rubio, Marco',
    'Christie, Christopher J.',
    'Kasich, John R.',
    'Paul, Rand',
]

totals = totals.reindex([name for name in arbitrary_order if name in totals.index])

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(totals.index, totals.values, color=PALETTE_WONG[5])
ax.set_title('Top 15 Candidates by Total Campaign Disbursements (2016)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Total disbursements ($)', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()