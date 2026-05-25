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
df = pd.read_csv(data_path, usecols=['Age'])
age = pd.to_numeric(df['Age'], errors='coerce').dropna()
age = age[(age >= 15) & (age <= 70)]

bin_edges = [15, 18, 21, 24, 27, 30, 35, 45, 55, 70]

bin_labels = ['15-18', '18-21', '21-24', '24-27', '27-30', '30-35', '35-45', '45-55', '55-70']

counts, _ = np.histogram(age, bins=bin_edges)

fig, ax = plt.subplots(figsize=(10, 6))

x_positions = np.arange(len(bin_labels))
ax.bar(x_positions, counts, color=PALETTE_WONG[3], edgecolor='white', width=0.8)

ax.set_xticks(x_positions)
ax.set_xticklabels(bin_labels, rotation=45, ha='right')

ax.set_title('Distribution of Developer Age (Stack Overflow 2020)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Age (years)', fontsize=12)
ax.set_ylabel('Number of respondents', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()