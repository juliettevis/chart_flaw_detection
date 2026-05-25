import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

col = "Estimated prevalence of TB (all forms) per 100 000 population"
data_2013 = df[df["Year"] == 2013][col].dropna()

fig, ax = plt.subplots(figsize=(10, 6))

bins = range(0, 1050, 50)
hist, bin_edges = np.histogram(data_2013, bins=bins)

# Select only the top 5 prevalence ranges but calculate percentages based on total
top_indices = np.argsort(hist)[-5:]
total_countries = hist.sum()

categories = []
values = []
for idx in sorted(top_indices):
    categories.append(f"{bin_edges[idx]}-{bin_edges[idx+1]}")
    values.append(hist[idx])

percentages = [(v/total_countries)*100 for v in values]

# Combine range and percentage as slice labels
combined_labels = [f'{pct:.1f}%' for pct in percentages]

wedges, texts = ax.pie(values, labels=combined_labels,
                       colors=PALETTE_WONG[:5], startangle=90,
                       labeldistance=0.6)

# Add "countries" unit to legend entries
categories_with_unit = [f'{cat} countries' for cat in categories]
ax.legend(wedges, categories_with_unit, title="TB Prevalence Range\n(per 100,000)",
          loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

ax.set_title("Distribution of TB Prevalence Rates Across Countries (2013)", fontsize=14, fontweight="bold", pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()