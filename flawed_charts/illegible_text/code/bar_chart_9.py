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

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

col = "Estimated prevalence of TB (all forms) per 100 000 population"
data_2013 = df[df["Year"] == 2013][col].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
bins = range(0, 1050, 50)
ax.hist(data_2013, bins=bins, color=PALETTE_WONG[3], edgecolor="white", linewidth=0.5)

ax.set_title("Distribution of TB Prevalence Rates Across Countries (2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("TB Prevalence per 100,000 Population", fontsize=12, labelpad=-20)
ax.set_ylabel("Number of Countries", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()