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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)

indistinguishable_colors = [
    "#CC79A7",
    "#C86FA0",
    "#D4849B",
]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts, autotexts = ax.pie(
    sales.values,
    labels=None,
    autopct="%1.1f%%",
    colors=indistinguishable_colors[:len(sales)],
    startangle=90,
    textprops={"fontsize": 11},
)
for t in autotexts:
    t.set_fontsize(10)

ax.legend(wedges, sales.index, loc="best", fontsize=10)

ax.set_title("Sales Distribution by Product Category (2023–2026)", fontsize=14, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()