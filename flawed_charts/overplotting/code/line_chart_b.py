import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'mortality.csv')
df = pd.read_csv(data_path, thousands=',')

usa = df[df["Country Code"] == "USA"].copy()
usa = usa[usa["Age Group"] != "All ages"]
usa["rate"] = pd.to_numeric(usa["Death Rate Per 100,000"], errors="coerce")
usa = usa.dropna(subset=["rate"])

fig, ax = plt.subplots(figsize=(10, 6))
for (age, sex), grp in usa.groupby(["Age Group", "Sex"]):
    grp = grp.sort_values("Year")
    ax.plot(grp["Year"], grp["rate"], color="#7f0e0e", linewidth=1.0, alpha=0.8)

ax.set_title("USA Death Rate per 100,000 Over Time — All Age Groups × Sexes", fontsize=14, fontweight="bold")
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Death rate per 100,000", fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
