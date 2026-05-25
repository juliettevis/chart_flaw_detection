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
country_col = "Country or territory name"

latest = df[df["Year"] == 2010].dropna(subset=[inc])
top15 = latest.nlargest(15, inc)[country_col].tolist()
sub = df[df[country_col].isin(top15)]

cmap = plt.get_cmap("tab20")
fig, ax = plt.subplots(figsize=(11, 6))
for i, country in enumerate(top15):
    grp = sub[sub[country_col] == country].sort_values("Year")
    ax.plot(grp["Year"], grp[inc], color=cmap(i % 20), linewidth=2, label=country)

ax.set_title("TB Incidence per 100,000 Over Time — Top 15 Countries", fontsize=14, fontweight="bold")
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Incidence per 100,000", fontsize=12)
ax.legend(fontsize=8, ncol=2, loc="upper right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
