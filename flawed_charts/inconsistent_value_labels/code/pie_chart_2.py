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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

orders = df.drop_duplicates("Order ID")
counts = orders.groupby("Ship Mode").size().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts, autotexts = ax.pie(
    counts.values,
    labels=None,
    autopct="%1.1f%%",
    colors=PALETTE_WONG[1:len(counts) + 1],
    startangle=90,
    textprops={"fontsize": 14},
)

total = counts.sum()
pcts = [v / total * 100 for v in counts.values]

formats = [
    lambda p: f"{p:.0f}%",
    lambda p: f"{p:.2f}%",
    lambda p: f"{p:.1f}%",
    lambda p: f"{p:.3f}%",
]
fontsizes = [18, 8, 13, 16]

for i, (t, p) in enumerate(zip(autotexts, pcts)):
    t.set_text(formats[i](p))
    t.set_fontsize(fontsizes[i])

ax.legend(wedges, counts.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)
ax.set_title("Orders by Shipping Method (2023–2026)", fontsize=16, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()