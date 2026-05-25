import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

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

male_data = us[us["Sex"] == "Male"]["Death Rate Per 100,000"].values
female_data = us[us["Sex"] == "Female"]["Death Rate Per 100,000"].values

fig, ax = plt.subplots(figsize=(10, 6))

line1, = ax.plot(range(len(age_order)), male_data,
                 marker="s", markersize=5, linewidth=1.8, color="#4393C3", label="Male")

ax.set_yscale("log")
ax.set_ylim(8, 20000)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_ylabel("Male Death Rate per 100,000", fontsize=12)
ax.tick_params(axis="y", labelsize=10)

ax2 = ax.twinx()
line2, = ax2.plot(range(len(age_order)), female_data,
                  marker="o", markersize=5, linewidth=1.8, color="#D6604D", label="Female")

ax2.set_yscale("log")
ax2.set_ylim(5, 11000)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax2.set_ylabel("Female Death Rate per 100,000", fontsize=12)
ax2.tick_params(axis="y", labelsize=10)

ax.set_xticks(range(len(age_order)))
ax.set_xticklabels([a.replace(" years", "") for a in age_order], rotation=45, ha="right", fontsize=10)
ax.set_title("Mortality Rate by Age Group and Sex (United States, 2010)",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Age Group", fontsize=12)

lines = [line1, line2]
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc="upper left", fontsize=11)

ax.spines["top"].set_visible(False)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()