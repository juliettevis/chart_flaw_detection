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

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(deaths.index, deaths.values, color=PALETTE_WONG[5], width=0.6)

ax.set_title("Estimated TB Deaths by WHO Region (2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("WHO Region", fontsize=12)
ax.tick_params(axis="x", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.set_yticks([])
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()