import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

# Map preferred positions to position groups
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
counts = df['Position Group'].dropna().value_counts()

# Order: Forward, Midfielder, Defender, Goalkeeper
order = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
counts = counts.reindex(order)

indistinguishable_colors = [
    '#009E73',
    '#00A876',
    '#00B27A',
    '#05956C',
]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts, autotexts = ax.pie(
    counts.values,
    labels=None,
    autopct="%1.1f%%",
    colors=indistinguishable_colors[:len(counts)],
    startangle=90,
    textprops={"fontsize": 11},
)
for t in autotexts:
    t.set_fontsize(10)

ax.legend(wedges, counts.index, loc="best", fontsize=10)

ax.set_title("Distribution of Players by Position Group", fontsize=14, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()