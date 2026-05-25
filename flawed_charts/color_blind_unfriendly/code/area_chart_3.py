import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

def position_group(pos_str):
    if pd.isna(pos_str):
        return None
    first_pos = pos_str.strip().split()[0]
    if first_pos == 'GK':
        return 'Goalkeeper'
    elif first_pos in ('CB', 'LB', 'RB', 'LWB', 'RWB', 'LCB', 'RCB'):
        return 'Defender'
    elif first_pos in ('CM', 'CDM', 'CAM', 'LM', 'RM', 'LCM', 'RCM', 'LDM', 'RDM'):
        return 'Midfielder'
    else:
        return 'Forward'

df['Position Group'] = df['Preferred Positions'].apply(position_group)
df = df.dropna(subset=['Position Group', 'Age'])
df = df[(df['Age'] >= 18) & (df['Age'] <= 40)]

groups = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
pivot = df.groupby(['Age', 'Position Group']).size().unstack(fill_value=0)
pivot = pivot.reindex(columns=groups, fill_value=0)
ages = pivot.index

fig, ax = plt.subplots(figsize=(10, 6))

colorblind_unfriendly_colors = ['#CC0000', '#009E73', '#E31A1C', '#2CA02C']

ax.stackplot(ages, [pivot[g] for g in groups], labels=groups, colors=colorblind_unfriendly_colors)

ax.set_title("Position Group Composition by Age (FIFA 18)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.set_xlim(ages[0], ages[-1])
ax.set_xticks(ages)
ax.set_ylim(bottom=0)
ax.legend(loc="upper right", fontsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()