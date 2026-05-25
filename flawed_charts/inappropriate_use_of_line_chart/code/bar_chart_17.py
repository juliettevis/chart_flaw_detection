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

fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(totals.index, totals.values, color=PALETTE_WONG[5], marker='o')
ax.set_title('Top 15 Candidates by Total Campaign Disbursements (2016)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Candidate', fontsize=12)
ax.set_ylabel('Total disbursements ($)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()