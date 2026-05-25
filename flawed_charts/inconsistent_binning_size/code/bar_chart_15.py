import argparse, sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'survey_results_public.csv')
df = pd.read_csv(data_path, usecols=['WorkWeekHrs'])
hrs = df['WorkWeekHrs'].dropna()
hrs = hrs[(hrs >= 10) & (hrs <= 80)]

bin_edges = [10, 15, 20, 25, 35, 42, 55, 80]

fig, ax = plt.subplots(figsize=(10, 6))

counts, _ = np.histogram(hrs, bins=bin_edges)

bin_labels = [f'{bin_edges[i]}-{bin_edges[i+1]}' for i in range(len(bin_edges)-1)]

x_positions = np.arange(len(bin_labels))
ax.bar(x_positions, counts, color=PALETTE_WONG[2], edgecolor='white', width=0.8)
ax.set_xticks(x_positions)
ax.set_xticklabels(bin_labels, fontsize=10)

ax.set_title('Distribution of Weekly Work Hours (Stack Overflow 2020)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Hours worked per week', fontsize=12)
ax.set_ylabel('Number of respondents', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()