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

counts = df['Nationality'].value_counts().head(10)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(counts.index, counts.values, color=PALETTE_WONG[5], width=0.6)

# Inconsistent labels: manually annotate each bar differently
label_formats = [
    ("1.6K", 16, "bold"),        # England: abbreviated, large, bold
    ("1,140", 9, "normal"),       # Germany: with comma separator, normal
    ("1019", 9, "normal"),        # Spain: no comma, normal
    ("978.0", 7, "normal"),       # France: one decimal place, small
    (None, 9, "normal"),          # Argentina: no label
    ("812", 14, "bold"),          # Brazil: large bold
    ("799.00", 7, "normal"),      # Italy: two decimal places, small
    (None, 9, "normal"),          # Colombia: no label
    ("469", 9, "normal"),         # Japan: plain integer
    ("0.429K", 8, "normal"),      # Netherlands: abbreviated differently
]

for bar, (label, fsize, fweight) in zip(bars, label_formats):
    if label is not None:
        ax.annotate(
            label,
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=fsize, fontweight=fweight
        )

ax.set_title("Number of FIFA 18 Players by Nationality (Top 10)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Nationality", fontsize=12)
ax.set_ylabel("Number of Players", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()