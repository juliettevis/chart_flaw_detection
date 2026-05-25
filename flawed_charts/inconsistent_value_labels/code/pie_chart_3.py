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

total = counts.values.sum()
percentages = counts.values / total * 100

fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts = ax.pie(
    counts.values,
    labels=None,
    autopct=None,
    colors=PALETTE_IBM[:len(counts)],
    startangle=90,
    textprops={"fontsize": 14},
)

# Manually add inconsistent labels
# Forward: 18.6% -> show with 2 decimal places, small font
# Midfielder: 39.9% -> show rounded to integer, large font
# Defender: 30.3% -> no label at all
# Goalkeeper: 11.3% -> show with 1 decimal place, medium font, rotated

label_formats = [
    (f"{percentages[0]:.2f}%", 8, 0),       # Forward: 2 decimal places, tiny font
    (f"{round(percentages[1])}%", 18, 0),    # Midfielder: integer, huge font
    (None, None, None),                       # Defender: no label
    (f"{percentages[3]:.1f}%", 13, 45),      # Goalkeeper: 1 decimal, rotated
]

for i, wedge in enumerate(wedges):
    label_text, fontsize, rotation = label_formats[i]
    if label_text is None:
        continue
    angle = (wedge.theta2 + wedge.theta1) / 2
    import numpy as np
    x = 0.7 * np.cos(np.radians(angle))
    y = 0.7 * np.sin(np.radians(angle))
    ax.text(x, y, label_text, ha='center', va='center', fontsize=fontsize, rotation=rotation)

ax.legend(wedges, counts.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

ax.set_title("Distribution of Players by Position Group", fontsize=16, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()