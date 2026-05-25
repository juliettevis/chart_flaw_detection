import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

# Exclude goalkeepers and missing values
def is_goalkeeper(pos_str):
    if pd.isna(pos_str):
        return True
    return pos_str.strip().split()[0] == 'GK'

df = df[~df['Preferred Positions'].apply(is_goalkeeper)]
df = df.dropna(subset=['Age', 'Sprint speed'])

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(df['Age'], df['Sprint speed'], color=PALETTE_WONG[5], alpha=0.15, s=8, edgecolors='none')

ax.set_title("Age vs Sprint Speed of FIFA 18 Players", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age", fontsize=12)
ax.set_ylabel("Sprint Speed (score out of 100)", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.set_xlim(left=15)
ax.set_ylim(bottom=0, top=105)

# Get current x-axis tick positions
xticks = ax.get_xticks()
# Create inconsistent x-axis labels
xlabels = []
for i, tick in enumerate(xticks):
    if i == 0:
        xlabels.append(f"{int(tick)}")
    elif i == 1:
        xlabels.append(f"{int(tick)}.0")
    elif i == 2:
        xlabels.append(f"TWENTY")
    elif i == 3:
        xlabels.append(f"{int(tick)} yrs")
    elif i == 4:
        xlabels.append(f"30")
    elif i == 5:
        xlabels.append(f"thirty-five")
    else:
        xlabels.append(f"{int(tick)}yo")
ax.set_xticklabels(xlabels)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()