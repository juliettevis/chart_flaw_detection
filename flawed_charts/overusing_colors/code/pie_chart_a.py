import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'superstore.csv')
df = pd.read_csv(data_path)

sales = df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False)
sales = sales.iloc[:-5]
cmap = plt.get_cmap("tab20")
colors = [cmap(i % 20) for i in range(len(sales))]

fig, ax = plt.subplots(figsize=(10, 8))
wedges, _, _ = ax.pie(
    sales.values, colors=colors, startangle=90,
    autopct="%1.1f%%", pctdistance=0.75,
    textprops={"fontsize": 12, "color": "black"},
)
ax.set_title("Share of Sales by Product Sub-Category (Superstore)", fontsize=14, fontweight="bold")
ax.legend(wedges, sales.index, title="Sub-Category", fontsize=11, title_fontsize=12,
          loc="center left", bbox_to_anchor=(1.0, 0.5))
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300, bbox_inches="tight")
plt.close()
