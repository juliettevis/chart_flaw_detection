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

sales_by_region = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    sales_by_region.values,
    labels=sales_by_region.index,
    autopct="%1.1f%%",
    colors=PALETTE_WONG[:len(sales_by_region)],
    startangle=90,
    pctdistance=0.75,
    labeldistance=1.05,
    textprops={'fontsize': 14}
)

for t in autotexts:
    t.set_fontsize(10)

ax.set_title("Sales Distribution by Region (2023–2026)", fontsize=14, fontweight="bold", pad=-20)
ax.legend(wedges, sales_by_region.index, title="Region", loc="center left",
          bbox_to_anchor=(0.92, 0.5), fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()