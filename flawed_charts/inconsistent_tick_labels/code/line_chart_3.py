import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

countries = ["India", "Nigeria", "China", "South Africa", "Brazil"]
subset = df[df["Country or territory name"].isin(countries)].copy()

fig, ax = plt.subplots(figsize=(10, 6))
for i, country in enumerate(countries):
    cdata = subset[subset["Country or territory name"] == country].sort_values("Year")
    ax.plot(cdata["Year"],
            cdata["Estimated number of deaths from TB (all forms, excluding HIV)"],
            marker="o", markersize=3, linewidth=1.8,
            color=PALETTE_CUSTOM[i], label=country)

ax.set_title("Estimated TB Deaths Over Time by Country (1990–2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Number of Deaths", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax.legend(loc="upper right", fontsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()

# Set inconsistent y-tick label formats
yticks = [0, 100000, 200000, 300000, 400000]
ax.set_yticks(yticks)
inconsistent_labels = ["0", "100,000", "200K", "300000.00", "400,000"]
ax.set_yticklabels(inconsistent_labels, fontsize=10)

plt.savefig(args.output_path, dpi=300)
plt.close()