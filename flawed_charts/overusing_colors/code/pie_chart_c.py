import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'mortality.csv')
df = pd.read_csv(data_path, thousands=',')

usa = df[(df["Country Code"] == "USA") & (df["Year"] == 2010) & (df["Sex"] == "Both")].copy()
usa = usa[usa["Age Group"] != "All ages"]
usa["deaths"] = pd.to_numeric(usa["Number of Deaths"], errors="coerce")
grp = usa.groupby("Age Group")["deaths"].sum().sort_values(ascending=False)
grp = grp[grp > 0]

sorted_vals = sorted(grp.values)
threshold = sorted_vals[11]

PALETTE = [
    (204/255, 121/255, 167/255), (230/255, 159/255, 0), (86/255, 180/255, 233/255),
    (0, 158/255, 115/255), (240/255, 228/255, 66/255), (0, 114/255, 178/255),
    (213/255, 94/255, 0), (100/255, 143/255, 1.0), (254/255, 97/255, 0),
    (220/255, 38/255, 127/255), (120/255, 94/255, 240/255), (150/255, 74/255, 139/255),
    (156/255, 156/255, 161/255), (122/255, 33/255, 221/255), (0.15, 0.45, 0.25),
    (0.55, 0.27, 0.07), (0.10, 0.10, 0.44), (0.85, 0.75, 0.20),
    (0.00, 0.55, 0.55), (0.40, 0.40, 0.40), (0.75, 0.35, 0.55), (0.35, 0.65, 0.85),
]

total = grp.sum()
def autopct(pct):
    value = pct / 100.0 * total
    return f"{pct:.1f}%" if value >= threshold else ""

fig, ax = plt.subplots(figsize=(10, 8))
wedges, _, _ = ax.pie(
    grp.values, colors=PALETTE[:len(grp)], startangle=90,
    autopct=autopct, pctdistance=0.75,
    textprops={"fontsize": 12, "color": "black"},
)
ax.set_title("USA Deaths by Age Group (2010)", fontsize=14, fontweight="bold")
ax.legend(wedges, grp.index, title="Age group", fontsize=11, title_fontsize=12,
          loc="center left", bbox_to_anchor=(1.0, 0.5))
ax.tick_params(axis="both", labelsize=10)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300, bbox_inches="tight")
plt.close()
