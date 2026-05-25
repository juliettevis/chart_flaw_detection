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

# Store original percentages for labels
original_total = deaths_2013.values.sum()
original_percentages = [(val/original_total)*100 for val in deaths_2013.values]

# Create misrepresented data for plotting
misrepresented_data = deaths_2013.copy()
misrepresented_data['South-East Asia'] = misrepresented_data['South-East Asia'] * 0.65  # Make smaller
misrepresented_data['Africa'] = misrepresented_data['Africa'] * 1.25  # Make larger
misrepresented_data['Eastern Mediterranean'] = misrepresented_data['Eastern Mediterranean'] * 0.5  # Make smaller

# Re-sort based on misrepresented values to maintain color order
misrepresented_sorted = misrepresented_data.sort_values(ascending=False)
color_order = [COLORS_6[list(deaths_2013.index).index(region)] for region in misrepresented_sorted.index]

fig, ax = plt.subplots(figsize=(11, 8))

wedges, texts, autotexts = ax.pie(
    misrepresented_sorted.values,
    labels=None,
    autopct=lambda p: f"{original_percentages[list(misrepresented_sorted.index).index(deaths_2013.index[int(round(p*len(deaths_2013)/100))])]:.1f}%",
    colors=color_order,
    startangle=90,
    pctdistance=0.75
)

# Override autopct with original percentages
for i, (at, orig_pct) in enumerate(zip(autotexts, [original_percentages[list(deaths_2013.index).index(region)] for region in misrepresented_sorted.index])):
    at.set_text(f"{orig_pct:.1f}%")
    at.set_fontsize(13)
    if orig_pct < 5:
        # Place label outside the slice with a connecting line
        ang = (wedges[i].theta2 + wedges[i].theta1) / 2
        import numpy as np
        x = np.cos(np.radians(ang))
        y = np.sin(np.radians(ang))
        at.set_position((1.15 * x, 1.05 * y))
        at.set_ha("center")

ax.set_title("Share of Global TB Deaths by WHO Region (2013)", fontsize=16, fontweight="bold", pad=16)
ax.legend(wedges, misrepresented_sorted.index, title="Region", loc="center left",
          bbox_to_anchor=(1.0, 0.5), fontsize=12)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()