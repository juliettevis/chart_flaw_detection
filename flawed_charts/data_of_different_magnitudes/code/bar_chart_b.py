import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'football.csv')
df = pd.read_csv(data_path)

top = df.nlargest(10, "Value (€)")[["Name", "Wage (€)", "Value (€)"]]

x = np.arange(len(top))
w = 0.4
fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - w/2, top["Wage (€)"], w, color="#2ca02c", label="Weekly wage (€)")
ax.bar(x + w/2, top["Value (€)"], w, color="#9467bd", label="Market value (€)")

ax.set_xticks(x)
ax.set_xticklabels(top["Name"], rotation=30, ha="right", fontsize=10)
ax.set_title("Wage vs Market Value — Top 10 Players by Value (FIFA 18)", fontsize=14, fontweight="bold")
ax.set_xlabel("Player", fontsize=12)
ax.set_ylabel("Amount (€)", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"€{x/1e6:,.0f}M"))
ax.tick_params(axis="y", labelsize=10)
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
