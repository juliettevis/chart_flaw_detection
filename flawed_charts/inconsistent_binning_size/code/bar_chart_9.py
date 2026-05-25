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

# Define custom unequal bin edges
custom_bins = [0, 50, 100, 150, 250, 400, 700, 1000]

# Calculate histogram with custom bins
counts, bin_edges = np.histogram(data_2013, bins=custom_bins)

# Create bar positions and widths
bin_labels = [f"{custom_bins[i]}-{custom_bins[i+1]}" for i in range(len(custom_bins)-1)]
x_pos = range(len(bin_labels))

# Plot bars
ax.bar(x_pos, counts, color=PALETTE_WONG[3], edgecolor="white", linewidth=0.5)

# Set x-axis labels to show bin ranges
ax.set_xticks(x_pos)
ax.set_xticklabels(bin_labels, rotation=0)

ax.set_title("Distribution of TB Prevalence Rates Across Countries (2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("TB Prevalence per 100,000 Population", fontsize=12)
ax.set_ylabel("Number of Countries", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

# Import numpy which is needed for histogram
import numpy as np

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()