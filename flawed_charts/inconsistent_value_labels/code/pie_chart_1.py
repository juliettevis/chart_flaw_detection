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

total = sales.sum()
pcts = (sales.values / total * 100)

fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts, autotexts = ax.pie(
    sales.values,
    labels=None,
    autopct="%1.1f%%",
    colors=PALETTE_IBM[:len(sales)],
    startangle=90,
    textprops={"fontsize": 14},
)

pct_formats = [
    f"{pcts[0]:.0f}%",
    f"{pcts[1]:.2f}%%"[:-1],
    f"{pcts[2]:.1f}%",
]

font_sizes = [18, 9, 13]

for i, (t, fmt, fs) in enumerate(zip(autotexts, pct_formats, font_sizes)):
    t.set_text(fmt)
    t.set_fontsize(fs)

ax.legend(wedges, sales.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

ax.set_title("Sales Distribution by Product Category (2023–2026)", fontsize=16, fontweight="bold", pad=16)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()