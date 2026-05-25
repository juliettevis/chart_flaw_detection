import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

region_labels = {
    "SEA": "South-East\nAsia", "AFR": "Africa", "WPR": "Western\nPacific",
    "EMR": "Eastern\nMediterranean", "EUR": "Europe", "AMR": "Americas"
}

deaths = df[df["Year"] == 2013].groupby("Region")[
    "Estimated number of deaths from TB (all forms, excluding HIV)"
].sum().sort_values(ascending=False)
deaths.index = deaths.index.map(region_labels)

# Calculate total for all regions
total_deaths = deaths.sum()

# Only include top 4 regions in pie chart
top4_deaths = deaths.iloc[:4]

# Calculate percentages relative to the FULL total (including omitted regions)
percentages = (top4_deaths.values / total_deaths) * 100

fig, ax = plt.subplots(figsize=(10, 6))

# Combine region name and percentage as slice labels
combined_labels = [f'{pct:.1f}%' for pct in percentages]

# Create pie chart with labels on slices
wedges, texts = ax.pie(top4_deaths.values, labels=combined_labels,
                       colors=PALETTE_WONG[:4], startangle=90,
                       labeldistance=0.6)

# Add legend with region names
ax.legend(wedges, top4_deaths.index, title="WHO Region",
          loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

ax.set_title("Estimated TB Deaths by WHO Region (2013)", fontsize=14, fontweight="bold", pad=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()