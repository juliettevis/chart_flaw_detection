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

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df["Sales"], df["Profit"], s=25, color="#d62728", alpha=1.0)

ax.set_title("Sales vs Profit per Order Line (Superstore, 2023–2026)", fontsize=14, fontweight="bold")
ax.set_xlabel("Sales ($)", fontsize=12)
ax.set_ylabel("Profit ($)", fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.axhline(0, color="black", linewidth=0.6)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
