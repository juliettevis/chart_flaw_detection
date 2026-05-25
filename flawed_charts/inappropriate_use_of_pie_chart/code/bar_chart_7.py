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

# Create overlapping age categories that double-count players
young_players = len(df[df["Age"] <= 25])  # 16-25
prime_age = len(df[(df["Age"] >= 23) & (df["Age"] <= 30)])  # 23-30 (overlaps with young)
experienced = len(df[df["Age"] >= 28])  # 28+ (overlaps with prime)
under_30 = len(df[df["Age"] < 30])  # All under 30 (overlaps with young and prime)

categories = ["Young (≤25)", "Prime (23-30)", "Experienced (28+)", "Under 30"]
values = [young_players, prime_age, experienced, under_30]

# Calculate percentages based on total players
total_players = len(df)
percentages = [(v / total_players) * 100 for v in values]

# Create pie chart with manual percentage labels
wedges, texts, autotexts = ax.pie(values, labels=None, colors=PALETTE_WONG[:4], 
                                  autopct=lambda pct: f'{pct:.1f}%',
                                  startangle=90)

# Override the auto-calculated percentages with our manual ones
for i, autotext in enumerate(autotexts):
    autotext.set_text(f'{percentages[i]:.1f}%')
    autotext.set_color('white')
    autotext.set_fontsize(10)

ax.legend(categories, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
ax.set_title("Distribution of FIFA 18 Player Ages", fontsize=14, fontweight="bold", pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()