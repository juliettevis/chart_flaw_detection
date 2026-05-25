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
prev = "Estimated prevalence of TB (all forms)"
deaths = "Estimated number of deaths from TB (all forms, excluding HIV)"
country_col = "Country or territory name"

china = df[df[country_col] == "China"].sort_values("Year")

fig, ax = plt.subplots(figsize=(11, 6))
ax.fill_between(china["Year"], china[pop], color="#17becf", alpha=0.5, label="Population")
ax.fill_between(china["Year"], china[prev], color="#9467bd", alpha=0.6, label="TB prevalence (cases)")
ax.fill_between(china["Year"], china[deaths], color="#d62728", alpha=0.7, label="TB deaths")

ax.set_title("China: Population vs TB Prevalence vs TB Deaths (1990–2013)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("People", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:,.0f}M"))
ax.legend(loc="upper left")
ax.tick_params(axis="both", labelsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
