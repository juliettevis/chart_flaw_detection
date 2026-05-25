import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

prod_sales = df.groupby(["Product ID", "Sub-Category"])["Sales"].sum().reset_index()
top = prod_sales.nlargest(30, "Sales").reset_index(drop=True)

subs = sorted(top["Sub-Category"].unique())
cmap = plt.get_cmap("tab20")
sub_colors = {s: cmap(i % 20) for i, s in enumerate(subs)}
bar_colors = [sub_colors[s] for s in top["Sub-Category"]]

fig, ax = plt.subplots(figsize=(12, 7))
ax.bar(range(len(top)), top["Sales"], color=bar_colors)
ax.set_title("Top 30 Products by Sales — Colored by Sub-Category (Superstore)", fontsize=14, fontweight="bold")
ax.set_xlabel("Product ID", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.set_xticks(range(len(top)))
ax.set_xticklabels(top["Product ID"], rotation=60, ha="right", fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

handles = [mpatches.Patch(color=sub_colors[s], label=s) for s in subs]
ax.legend(handles=handles, title="Sub-Category", fontsize=8, ncol=2, loc="upper right")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
