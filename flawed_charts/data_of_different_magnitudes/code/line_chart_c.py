import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'mortality.csv')
df = pd.read_csv(data_path)
us = df[(df['Country Name'] == 'United States') & (df['Sex'] == 'Both')].copy()
us['Death Rate Per 100,000'] = pd.to_numeric(
    us['Death Rate Per 100,000'].astype(str).str.replace(',', ''), errors='coerce')

all_ages = us[us['Age Group'] == 'All ages'].sort_values('Year')
infants = us[us['Age Group'] == '0-6 days'].sort_values('Year')

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(infants['Year'], infants['Death Rate Per 100,000'], color=PALETTE_WONG[6],
        linewidth=2, marker='o', label='0–6 days')
ax.plot(all_ages['Year'], all_ages['Death Rate Per 100,000'], color=PALETTE_WONG[5],
        linewidth=2, marker='s', label='All ages')

ax.set_title('USA Death Rate by Age Group (per 100,000)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Death rate per 100,000', fontsize=12)
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
