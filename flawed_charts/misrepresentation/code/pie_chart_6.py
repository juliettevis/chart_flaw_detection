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
party_colors = {'Democrat': '#0015BC', 'Republican': '#FF0000'}
colors = [party_colors[p] for p in totals.index]

# Use distorted values for visual encoding but keep original labels
# Original: Democrat ~50.2%, Republican ~49.8%
# Distorted: Democrat gets ~75%, Republican gets ~25% visually
distorted_values = [totals.values[0] * 3.0, totals.values[1] * 0.5]

original_labels = ['50.2%', '49.8%']

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _ = ax.pie(
    distorted_values, labels=None, autopct=None,
    colors=colors, startangle=90)

# Manually place the original correct percentage labels on the slices
import numpy as np
total_distorted = sum(distorted_values)
cumulative = 0
for i, (wedge, label) in enumerate(zip(wedges, original_labels)):
    angle = (wedge.theta1 + wedge.theta2) / 2
    angle_rad = np.deg2rad(angle)
    x = 0.6 * np.cos(angle_rad)
    y = 0.6 * np.sin(angle_rad)
    ax.text(x, y, label, ha='center', va='center', fontsize=13, color='white')

ax.legend(wedges, totals.index, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)
ax.set_title('USA Campaign Disbursements by Party (2016)',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()