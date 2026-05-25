import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

top_nats = df["Nationality"].value_counts().head(30).index
sub = df[df["Nationality"].isin(top_nats)]
pivot = sub.groupby(["Age", "Nationality"])["Overall"].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
for nat, grp in pivot.groupby("Nationality"):
    grp = grp.sort_values("Age")
    ax.plot(grp["Age"], grp["Overall"], color="#ff7f0e", linewidth=1.0, alpha=0.8)

ax.set_title("Average Overall Rating by Age — Top 30 Nationalities", fontsize=14, fontweight="bold")
ax.set_xlabel("Age", fontsize=12)
ax.set_ylabel("Mean overall rating", fontsize=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
