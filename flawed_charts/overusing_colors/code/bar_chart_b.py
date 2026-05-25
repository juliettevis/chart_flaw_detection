import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

top = df.nlargest(30, "Value (€)")[["Name", "Value (€)", "Nationality"]].reset_index(drop=True)

nats = sorted(top["Nationality"].unique())
cmap = plt.get_cmap("tab20")
nat_colors = {n: cmap(i % 20) for i, n in enumerate(nats)}
bar_colors = [nat_colors[n] for n in top["Nationality"]]

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(top["Name"], top["Value (€)"], color=bar_colors)
ax.set_title("Top 30 FIFA 18 Players by Market Value — Colored by Nationality", fontsize=14, fontweight="bold")
ax.set_xlabel("Player", fontsize=12)
ax.set_ylabel("Market value (€)", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x:,.0f}"))
plt.xticks(rotation=45, ha="right", fontsize=10)

handles = [mpatches.Patch(color=nat_colors[n], label=n) for n in nats]
ax.legend(handles=handles, title="Nationality", fontsize=8, ncol=2, loc="upper right")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
