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

indistinguishable_colors = [
    "#CC79A7",
    "#C96FA0",
    "#D08AB0",
    "#C5749F",
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

ax.legend(wedges, counts.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
ax.set_title("Orders by Shipping Method (2023–2026)", fontsize=14, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()