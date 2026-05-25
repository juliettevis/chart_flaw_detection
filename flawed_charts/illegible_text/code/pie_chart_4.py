import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

# Custom colors for 6 regions — avoids the two similar purples in PALETTE_CUSTOM
COLORS_6 = [
    PALETTE_CUSTOM[0],                     # Blue
    PALETTE_CUSTOM[1],                     # Orange
    PALETTE_CUSTOM[2],                     # Red
    (0, 158/255, 115/255),                 # Teal (from Wong palette)
    PALETTE_CUSTOM[4],                     # Gray
    (180/255, 130/255, 40/255),            # Dark gold
]

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

region_labels = {
    "AFR": "Africa", "SEA": "South-East Asia", "EMR": "Eastern Mediterranean",
    "WPR": "Western Pacific", "EUR": "Europe", "AMR": "Americas"
}

deaths_2013 = df[df["Year"] == 2013].groupby("Region")[
    "Estimated number of deaths from TB (all forms, excluding HIV)"
].sum()
deaths_2013 = deaths_2013.rename(index=region_labels)
deaths_2013 = deaths_2013.sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(11, 8))

wedges, texts, autotexts = ax.pie(
    deaths_2013.values,
    labels=None,
    autopct="%1.1f%%",
    colors=COLORS_6[:len(deaths_2013)],
    startangle=90,
    pctdistance=0.75
)

for at in autotexts:
    at.set_fontsize(13)

ax.set_title("Share of Global Tuberculosis Deaths by World Health Organization Region (Year Two Thousand and Thirteen)", fontsize=16, pad=-10)
ax.legend(wedges, deaths_2013.index, title="Region", loc="center left",
          bbox_to_anchor=(1.0, 0.5), fontsize=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()