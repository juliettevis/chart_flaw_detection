import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

top = df.nlargest(50, "Overall").reset_index(drop=True)
x = top.index.values

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(x, top["Wage (€)"], color="#2ca02c", s=36, label="Weekly wage")
ax.scatter(x, top["Value (€)"], color="#9467bd", s=36, label="Market value")

ax.set_title("Top 50 FIFA 18 Players — Wage vs Market Value (same y-axis)", fontsize=14, fontweight="bold")
ax.set_xlabel("Player rank by Overall", fontsize=12)
ax.set_ylabel("Amount ($)", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:,.0f}M"))
ax.tick_params(axis="both", labelsize=10)
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
