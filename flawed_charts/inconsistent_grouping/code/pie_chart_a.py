import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'superstore.csv')
df = pd.read_csv(data_path)

tech = df[df['Category'] == 'Technology'].groupby('Sub-Category')['Sales'].sum()
furn_total = df[df['Category'] == 'Furniture']['Sales'].sum()
office_total = df[df['Category'] == 'Office Supplies']['Sales'].sum()

labels = list(tech.index) + ['Furniture', 'Office Supplies']
sizes = list(tech.values) + [furn_total, office_total]

colors = [PALETTE_WONG[0], PALETTE_WONG[1], PALETTE_WONG[2], PALETTE_WONG[3],
          PALETTE_WONG[5], PALETTE_WONG[6]]

fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                   autopct='%1.1f%%', startangle=140, pctdistance=0.75)
for t in autotexts:
    t.set_fontsize(9)

ax.set_title('Sales by Category (Superstore)', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
