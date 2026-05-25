import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

inc = "Estimated incidence (all forms) per 100 000 population"
mort = "Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population"
sub = df[[inc, mort]].dropna()

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(sub[inc], sub[mort], s=30, color="#2ca02c", alpha=1.0)

ax.set_title("TB Incidence vs Mortality per 100,000 (all countries, 1990–2013)", fontsize=13, fontweight="bold")
ax.set_xlabel("Incidence per 100,000", fontsize=12)
ax.set_ylabel("Mortality per 100,000", fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
