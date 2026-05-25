import argparse, sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Housing.csv')
df = pd.read_csv(data_path)
df = df[df['bedrooms'].isin([2, 3, 4])]
pivot = df.groupby(['bedrooms', 'furnishingstatus'])['price'].mean().unstack()
pivot = pivot[['furnished', 'semi-furnished', 'unfurnished']]

x = np.arange(len(pivot.index))
width = 0.25

fig, ax = plt.subplots(figsize=(11, 6))

# Plot Furnished and Semi-furnished on primary y-axis
bars1 = ax.bar(x - width, pivot['furnished'], width, color=PALETTE_WONG[5], label='Furnished')
bars2 = ax.bar(x, pivot['semi-furnished'], width, color=PALETTE_WONG[1], label='Semi-furnished')

ax.set_xticks(x)
ax.set_xticklabels([f'{b} bedrooms' for b in pivot.index])
ax.set_title('Average House Price by Bedrooms and Furnishing Status',
             fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Average price – Furnished & Semi-furnished (€)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1e6:.1f}M'))
ax.set_ylim(0, 8e6)
ax.spines['top'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)

# Secondary y-axis for Unfurnished — scaled to visually align with others
ax2 = ax.twinx()
bars3 = ax2.bar(x + width, pivot['unfurnished'], width, color=PALETTE_WONG[3], label='Unfurnished')

# Set secondary axis limits so unfurnished bars appear similar in height to the others,
# creating a false impression of similar scale
ax2.set_ylim(2_000_000, 5_500_000)
ax2.set_ylabel('Average price – Unfurnished (€)', fontsize=12)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1e6:.2f}M'))
ax2.spines['top'].set_visible(False)

# Combined legend
handles1, labels1 = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax.legend(handles1 + handles2, labels1 + labels2, fontsize=10)

plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()