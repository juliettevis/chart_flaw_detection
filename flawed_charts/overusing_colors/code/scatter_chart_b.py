import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

subs = sorted(df["Sub-Category"].unique())
cmap = plt.get_cmap("tab20")

fig, ax = plt.subplots(figsize=(11, 7))
for i, s in enumerate(subs):
    g = df[df["Sub-Category"] == s]
    ax.scatter(g["Sales"], g["Profit"], color=cmap(i % 20), s=18, alpha=0.7, label=s)

ax.set_title("Sales vs Profit per Order by Sub-Category", fontsize=14, fontweight="bold")
ax.set_xlabel("Sales ($)", fontsize=12)
ax.set_ylabel("Profit ($)", fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.axhline(0, color="black", linewidth=0.5)
ax.legend(fontsize=8, ncol=2, loc="lower right")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
