import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

pop = "Estimated total population number"
deaths = "Estimated number of deaths from TB (all forms, excluding HIV)"
country_col = "Country or territory name"

sub = df[df["Year"] == 2010].dropna(subset=[pop, deaths])
top = sub.nlargest(10, pop)[[country_col, pop, deaths]]

x = np.arange(len(top))
w = 0.4
fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - w/2, top[pop], w, color="#17becf", label="Population")
ax.bar(x + w/2, top[deaths], w, color="#d62728", label="TB deaths")

ax.set_xticks(x)
ax.set_xticklabels(top[country_col], rotation=30, ha="right")
ax.set_title("Population vs TB Deaths — 10 Most Populous Countries (2010)", fontsize=14, fontweight="bold")
ax.set_ylabel("People", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
