import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

inc_col = "Estimated incidence (all forms) per 100 000 population"
country_col = "Country or territory name"

fig, ax = plt.subplots(figsize=(10, 6))
for country, grp in df.groupby(country_col):
    grp = grp.sort_values("Year")
    ax.plot(grp["Year"], grp[inc_col], color="#1f77b4", linewidth=1.0, alpha=0.8)

ax.set_title("TB Incidence per 100,000 Over Time — Every Country (1990–2013)", fontsize=13, fontweight="bold")
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Incidence per 100,000", fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
