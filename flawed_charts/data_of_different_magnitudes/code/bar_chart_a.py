import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

agg = df.groupby("Sub-Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
agg = agg.sort_values("Sales", ascending=False).head(10)

x = np.arange(len(agg))
w = 0.4
fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - w/2, agg["Sales"], w, color="#1f77b4", label="Sales")
ax.bar(x + w/2, agg["Profit"], w, color="#ff7f0e", label="Profit")

ax.set_xticks(x)
ax.set_xticklabels(agg.index, rotation=30, ha="right")
ax.set_title("Sales vs Profit by Sub-Category (Superstore, Top 10)", fontsize=14, fontweight="bold")
ax.set_ylabel("Amount ($)", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.axhline(0, color="black", linewidth=0.5)
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
