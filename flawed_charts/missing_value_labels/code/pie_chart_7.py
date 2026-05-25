import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         '2016_presidential_candidate_expenditures.csv')
df = pd.read_csv(data_path).dropna(subset=['disb_desc'])
totals = df.groupby('disb_desc')['disb_amt'].sum().nlargest(5)

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _ = ax.pie(
    totals.values, labels=None, autopct=None,
    colors=PALETTE_IBM[:len(totals)], startangle=90, textprops={'fontsize': 14})
ax.legend(wedges, totals.index, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=11)
ax.set_title('Campaign Disbursements — Top 5 Categories (2016)',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()