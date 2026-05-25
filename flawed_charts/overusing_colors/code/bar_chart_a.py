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

city_sales = df.groupby(["City", "State/Province"])["Sales"].sum().reset_index()
top = city_sales.nlargest(25, "Sales").reset_index(drop=True)

states = sorted(top["State/Province"].unique())
cmap = plt.get_cmap("tab20")
state_colors = {s: cmap(i % 20) for i, s in enumerate(states)}
bar_colors = [state_colors[s] for s in top["State/Province"]]

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(top["City"], top["Sales"], color=bar_colors)
ax.set_title("Total Sales by Top 25 Cities — Colored by State (Superstore)", fontsize=14, fontweight="bold")
ax.set_xlabel("City", fontsize=12)
ax.set_ylabel("Sales ($)", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.xticks(rotation=45, ha="right", fontsize=10)

handles = [mpatches.Patch(color=state_colors[s], label=s) for s in states]
ax.legend(handles=handles, title="State", fontsize=8, ncol=2, loc="upper right")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
