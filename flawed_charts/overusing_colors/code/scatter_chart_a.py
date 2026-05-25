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
cmap = plt.get_cmap("gist_rainbow")

fig, ax = plt.subplots(figsize=(11, 7))
for i, nat in enumerate(top_nats):
    g = sub[sub["Nationality"] == nat]
    ax.scatter(g["Overall"], g["Potential"], color=cmap(i / 20), s=18, alpha=0.7, label=nat)

ax.set_title("FIFA 18 Overall vs Potential Rating by Nationality (Top 20 countries)", fontsize=14, fontweight="bold")
ax.set_xlabel("Overall rating", fontsize=12)
ax.set_ylabel("Potential rating", fontsize=12)
ax.legend(fontsize=8, ncol=2, loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
