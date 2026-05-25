import argparse
import os
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
hiv_deaths = "Estimated number of deaths from TB in people who are HIV-positive"
country_col = "Country or territory name"

india = df[df[country_col] == "India"].sort_values("Year")

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(india["Year"], india[pop], marker="o", color="#1f77b4", label="Population")
ax.plot(india["Year"], india[deaths], marker="s", color="#d62728", label="TB deaths")
ax.plot(india["Year"], india[hiv_deaths], marker="^", color="#2ca02c", label="HIV+ TB deaths")

ax.set_title("India: Population vs TB Deaths vs HIV+ TB Deaths (1990–2013)", fontsize=13, fontweight="bold")
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("People", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
