import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

countries = ["India", "Nigeria", "China", "South Africa", "Brazil"]
subset = df[df["Country or territory name"].isin(countries)].copy()

fig, ax = plt.subplots(figsize=(10, 6))

lines = []

# Plot India, Nigeria, China, South Africa on primary axis
for i, country in enumerate(["India", "Nigeria", "China", "South Africa"]):
    cdata = subset[subset["Country or territory name"] == country].sort_values("Year")
    line, = ax.plot(cdata["Year"],
            cdata["Estimated number of deaths from TB (all forms, excluding HIV)"],
            marker="o", markersize=3, linewidth=1.8,
            color=PALETTE_CUSTOM[i], label=country)
    lines.append(line)

# Plot Brazil on secondary axis
ax2 = ax.twinx()
brazil_data = subset[subset["Country or territory name"] == "Brazil"].sort_values("Year")
line_brazil, = ax2.plot(brazil_data["Year"],
        brazil_data["Estimated number of deaths from TB (all forms, excluding HIV)"],
        marker="o", markersize=3, linewidth=1.8,
        color=PALETTE_CUSTOM[4], label="Brazil")
lines.append(line_brazil)

# Set primary axis limits — India ranges ~240k–425k
ax.set_ylim(0, 500000)

# Set secondary axis limits to make Brazil (~5k–15k) appear to track India visually
# Brazil values ~5000–15000; we scale so that 15000 maps to ~425000 visually
# Secondary axis range: set so Brazil's line overlaps with India's trajectory
ax2.set_ylim(0, 15000)

ax.set_title("Estimated TB Deaths Over Time by Country (1990–2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Number of Deaths", fontsize=12)
ax2.set_ylabel("Brazil – Number of Deaths", fontsize=12)
ax.tick_params(axis="both", labelsize=10)
ax2.tick_params(axis="y", labelsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

ax.spines["top"].set_visible(False)

labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc="upper right", fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()