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

# Use only top 5 candidates but compute percentages relative to full total of all 15
top5 = totals.nlargest(5)
full_total = totals.sum()

# Manually compute percentages relative to full total (will sum to less than 100%)
percentages = (top5 / full_total * 100)
labels = [f'{p:.1f}%' for p in percentages]

colors = PALETTE_WONG[:5]

fig, ax = plt.subplots(figsize=(10, 7))
wedges, texts = ax.pie(
    top5.values,
    labels=labels,
    colors=colors,
    startangle=140,
    textprops={'fontsize': 11}
)

ax.set_title('Top 5 Candidates — Share of Campaign Disbursements (2016)',
             fontsize=14, fontweight='bold', pad=12)

ax.legend(wedges, top5.index, title="Candidate", loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()