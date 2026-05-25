import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

top10 = (df[df["Year"] == 2013]
         .nlargest(10, "Estimated prevalence of TB (all forms) per 100 000 population")
         .set_index("Country or territory name")
         ["Estimated prevalence of TB (all forms) per 100 000 population"]
         .sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(range(len(top10)), top10.values, color=PALETTE_WONG[0], width=0.6)

label_formats = [
    (f"0.9K", 14, False),       # index 0: Swaziland ~945 -> abbreviated
    (f"{906:.2f}", 9, False),    # index 1: Djibouti -> 2 decimal places
    (f"802", 9, True),           # index 2: Timor-Leste -> bold, no decimals
    None,                        # index 3: Kiribati -> no label
    (f"{715:.1f}", 7, False),    # index 4: Cambodia -> 1 decimal, small font
    None,                        # index 5: South Africa -> no label
    (f"651.00", 9, False),       # index 6: Namibia -> 2 decimals
    (f"0.613K", 16, False),      # index 7: Lesotho -> abbreviated, large font
    (f"578", 9, False),          # index 8: Gabon -> plain integer
    (f"{559:.2f}", 6, False),    # index 9: Mozambique -> 2 decimals, tiny font
]

vals = list(top10.values)
for i, (bar, val) in enumerate(zip(bars, vals)):
    fmt = label_formats[i]
    if fmt is None:
        continue
    label_text, fsize, bold = fmt
    weight = "bold" if bold else "normal"
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
            label_text, ha="center", va="bottom", fontsize=fsize, fontweight=weight)

ax.set_xticks(range(len(top10)))
ax.set_xticklabels(top10.index, rotation=35, ha="right", fontsize=9)
ax.set_title("Top 10 Countries by TB Prevalence per 100,000 (2013)", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Country", fontsize=12)
ax.set_ylabel("Prevalence per 100,000", fontsize=12)
ax.tick_params(axis="y", labelsize=10)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()