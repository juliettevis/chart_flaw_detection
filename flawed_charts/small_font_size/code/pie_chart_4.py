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

# Move labels outside for small slices (<5%)
total = deaths_2013.values.sum()
for i, (at, val) in enumerate(zip(autotexts, deaths_2013.values)):
    at.set_fontsize(3)
    if val / total < 0.05:
        # Place label outside the slice with a connecting line
        ang = (wedges[i].theta2 + wedges[i].theta1) / 2
        import numpy as np
        x = np.cos(np.radians(ang))
        y = np.sin(np.radians(ang))
        at.set_position((1.15 * x, 1.05 * y))
        at.set_ha("center")

ax.set_title("Share of Global TB Deaths by WHO Region (2013)", fontsize=5, fontweight="bold", pad=16)
ax.legend(wedges, deaths_2013.index, title="Region", loc="center left",
          bbox_to_anchor=(1.0, 0.5), fontsize=3, title_fontsize=3)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()