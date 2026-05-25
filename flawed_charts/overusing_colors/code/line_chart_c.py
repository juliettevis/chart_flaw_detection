import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

top_nats = df["Nationality"].value_counts().head(20).index.tolist()
sub = df[df["Nationality"].isin(top_nats)]
pivot = sub.groupby(["Age", "Nationality"])["Overall"].mean().unstack()
pivot = pivot[top_nats]

cmap = plt.get_cmap("tab20")

fig, ax = plt.subplots(figsize=(11, 6))
for i, nat in enumerate(pivot.columns):
    ax.plot(pivot.index, pivot[nat], color=cmap(i % 20), linewidth=1.8, label=nat)

ax.set_title("Average Overall Rating by Age — Top 20 Nationalities (FIFA 18)", fontsize=14, fontweight="bold")
ax.set_xlabel("Age", fontsize=12)
ax.set_ylabel("Mean Overall rating", fontsize=12)
ax.legend(fontsize=8, ncol=2, loc="lower right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
