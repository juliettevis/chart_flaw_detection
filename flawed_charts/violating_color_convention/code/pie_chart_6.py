import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         '2016_presidential_candidate_expenditures.csv')
df = pd.read_csv(data_path).dropna(subset=['cand_nm'])
democrats = {'Sanders, Bernard', 'Clinton, Hillary Rodham', "O'Malley, Martin Joseph"}
republicans = {"Cruz, Rafael Edward 'Ted'", 'Carson, Benjamin S.', 'Trump, Donald J.',
               'Rubio, Marco', 'Bush, Jeb', 'Kasich, John R.', 'Paul, Rand',
               'Walker, Scott', 'Fiorina, Carly', 'Christie, Christopher J.',
               'Graham, Lindsey O.', 'Huckabee, Mike'}
df['Party'] = df['cand_nm'].map(
    lambda n: 'Democrat' if n in democrats else ('Republican' if n in republicans else None))
df = df.dropna(subset=['Party'])
totals = df.groupby('Party')['disb_amt'].sum()
party_colors = {'Democrat': '#FF0000', 'Republican': '#0015BC'}
colors = [party_colors[p] for p in totals.index]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _, autotexts = ax.pie(
    totals.values, labels=None, autopct='%1.1f%%',
    colors=colors, startangle=90, textprops={'fontsize': 14, 'color': 'white'})
for t in autotexts:
    t.set_fontsize(13)
ax.legend(wedges, totals.index, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)
ax.set_title('USA Campaign Disbursements by Party (2016)',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()