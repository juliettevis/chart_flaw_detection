import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

counts = df["Nationality"].value_counts().head(20)

PALETTE = [
    (204/255, 121/255, 167/255),
    (230/255, 159/255, 0),
    (86/255, 180/255, 233/255),
    (0, 158/255, 115/255),
    (240/255, 228/255, 66/255),
    (0, 114/255, 178/255),
    (213/255, 94/255, 0),
    (100/255, 143/255, 1.0),
    (254/255, 97/255, 0),
    (220/255, 38/255, 127/255),
    (120/255, 94/255, 240/255),
    (150/255, 74/255, 139/255),
    (156/255, 156/255, 161/255),
    (122/255, 33/255, 221/255),
    (0.15, 0.45, 0.25),
    (0.55, 0.27, 0.07),
    (0.10, 0.10, 0.44),
    (0.85, 0.75, 0.20),
    (0.00, 0.55, 0.55),
    (0.40, 0.40, 0.40),
]

total = counts.sum()
pcts = counts.values / total * 100
big_mask = np.zeros(len(counts), dtype=bool)
big_mask[:10] = True

fig, ax = plt.subplots(figsize=(11, 8))
wedges, _ = ax.pie(counts.values, colors=PALETTE, startangle=90)

for i, w in enumerate(wedges):
    ang = (w.theta1 + w.theta2) / 2.0
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    if big_mask[i]:
        ax.text(0.7 * x, 0.7 * y, f"{pcts[i]:.1f}%", ha="center", va="center",
                fontsize=12, color="black")

for i in range(len(counts)):
    if big_mask[i]:
        continue
    w = wedges[i]
    ang = (w.theta1 + w.theta2) / 2.0
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    ha = "left" if x >= 0 else "right"
    ax.text(1.05 * x, 1.05 * y, f"{pcts[i]:.1f}%",
            ha=ha, va="center", fontsize=11)

ax.set_title("Player Share by Nationality (Top 20, FIFA 18)", fontsize=14, fontweight="bold")
ax.legend(wedges, counts.index, title="Nationality", fontsize=11, title_fontsize=12,
          loc="center left", bbox_to_anchor=(1.15, 0.5))
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300, bbox_inches="tight")
plt.close()
