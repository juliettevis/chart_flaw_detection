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

fig, ax = plt.subplots(figsize=(10, 6))
bins = range(16, 44, 2)
ax.hist(df["Age"], bins=bins, color=PALETTE_WONG[5], edgecolor="white", linewidth=0.5)

ax.set_title("Distribution of FIFA 18 Player Ages", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age (years)", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

# Get current y-tick locations
yticks = ax.get_yticks()
# Create inconsistent formatting for y-axis labels
inconsistent_labels = []
for i, val in enumerate(yticks):
    if i == 0:
        inconsistent_labels.append(f"{int(val)}")
    elif i == 1:
        inconsistent_labels.append(f"{int(val):,}")
    elif i == 2:
        inconsistent_labels.append(f"{val:.1f}")
    elif i == 3:
        inconsistent_labels.append(f"{int(val/1000)}K")
    elif i == 4:
        inconsistent_labels.append(f"{int(val):,}")
    elif i == 5:
        inconsistent_labels.append(f"{val:.0f}.0")
    else:
        inconsistent_labels.append(f"{int(val)}")

ax.set_yticklabels(inconsistent_labels)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()