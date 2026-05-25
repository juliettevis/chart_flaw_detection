import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'mortality.csv')
df = pd.read_csv(data_path)
df["Death Rate Per 100,000"] = df["Death Rate Per 100,000"].str.replace(",", "").astype(float)

us = df[(df["Country Code"] == "USA") & (df["Year"] == 2010) &
        (df["Age Group"] != "All ages")].copy()

age_order = ["1-4 years", "5-9 years", "10-14 years", "15-19 years",
             "20-24 years", "25-29 years", "30-34 years", "35-39 years",
             "40-44 years", "45-49 years", "50-54 years", "55-59 years",
             "60-64 years", "65-69 years", "70-74 years", "75-79 years", "80+ years"]

us = us[us["Age Group"].isin(age_order)]
us["Age Group"] = pd.Categorical(us["Age Group"], categories=age_order, ordered=True)
us = us.sort_values("Age Group")

fig, ax = plt.subplots(figsize=(10, 6))

categorical_colors_male = ["red", "blue", "green", "orange", "purple", "cyan", "magenta",
                            "brown", "lime", "navy", "gold", "teal", "crimson", "indigo",
                            "darkorange", "darkgreen", "hotpink"]
categorical_colors_female = ["blue", "green", "orange", "purple", "cyan", "magenta", "red",
                              "lime", "navy", "gold", "teal", "crimson", "indigo", "darkorange",
                              "darkgreen", "hotpink", "brown"]

for sex, colors, marker, label in [("Male", categorical_colors_male, "s", "Male"),
                                    ("Female", categorical_colors_female, "o", "Female")]:
    sdata = us[us["Sex"] == sex]
    xvals = list(range(len(age_order)))
    yvals = sdata["Death Rate Per 100,000"].values

    for i in range(len(xvals) - 1):
        ax.plot([xvals[i], xvals[i+1]], [yvals[i], yvals[i+1]],
                color=colors[i], linewidth=1.8)
    for i in range(len(xvals)):
        ax.plot(xvals[i], yvals[i], marker=marker, markersize=5, color=colors[i],
                label=label if i == 0 else "")

ax.set_xticks(range(len(age_order)))
ax.set_xticklabels([a.replace(" years", "") for a in age_order], rotation=45, ha="right", fontsize=10)
ax.set_title("Mortality Rate by Age Group and Sex (United States, 2010)",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age Group", fontsize=12)
ax.set_ylabel("Death Rate per 100,000", fontsize=12)
ax.tick_params(axis="y", labelsize=10)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend(loc="upper left", fontsize=11)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()