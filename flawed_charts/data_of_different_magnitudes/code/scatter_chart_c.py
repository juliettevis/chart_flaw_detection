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

prev = "Estimated prevalence of TB (all forms)"
inc_cases = "Estimated number of incident cases (all forms)"
country_col = "Country or territory name"

sub = df[df["Year"] == 2010].dropna(subset=[prev, inc_cases]).reset_index(drop=True)
x = sub.index.values

# Colors inspired by chart_utils PALETTE_CUSTOM / Wong
C_PREV = (150/255, 74/255, 139/255)   # purple (Custom)
C_INC = (228/255, 37/255, 54/255)     # red (Custom)

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(x, sub[prev], color=C_PREV, s=20, alpha=0.8, label="TB prevalence")
ax.scatter(x, sub[inc_cases], color=C_INC, s=20, alpha=0.8, label="Incident cases")

ax.set_title("TB Prevalence vs Incident Cases per Country (2010)", fontsize=14, fontweight="bold")
ax.set_xlabel("Country index", fontsize=12)
ax.set_ylabel("Amount of cases", fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:,.1f}M" if x >= 1e6 else f"{x/1e3:,.0f}K"))
ax.tick_params(axis="both", labelsize=10)
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
