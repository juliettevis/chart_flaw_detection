import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

data_2013 = df[df["Year"] == 2013].dropna(subset=[
    "Estimated prevalence of TB (all forms) per 100 000 population",
    "Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population"
])

fig, ax = plt.subplots(figsize=(10, 6))

x_data = data_2013["Estimated prevalence of TB (all forms) per 100 000 population"]
y_data = data_2013["Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population"]

ax.scatter(
    x_data,
    y_data,
    s=30, alpha=0.6, color=PALETTE_WONG[5], edgecolors="white", linewidth=0.3
)

# Add misleading trend line
coefficients = np.polyfit(x_data, y_data, 1)
polynomial = np.poly1d(coefficients)
x_line = np.linspace(x_data.min(), x_data.max(), 100)
y_line = polynomial(x_line)
ax.plot(x_line, y_line, color='red', linewidth=2, zorder=10)

ax.set_title("TB Prevalence vs Mortality Rate by Country (2013)",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Prevalence per 100,000", fontsize=12)
ax.set_ylabel("Mortality per 100,000", fontsize=12)
ax.tick_params(axis="both", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()