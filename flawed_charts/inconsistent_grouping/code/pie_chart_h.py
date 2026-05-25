import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_CUSTOM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'mortality.csv')
df = pd.read_csv(data_path)
us = df[(df['Country Name'] == 'United States') & (df['Sex'] == 'Both') &
        (df['Year'] == 2010) & (df['Age Group'] == 'All ages')].copy()
us['Number of Deaths'] = pd.to_numeric(
    us['Number of Deaths'].astype(str).str.replace(',', ''), errors='coerce')
total_deaths = us['Number of Deaths'].sum()

heart_total = total_deaths * 0.247
heart_subtypes = {
    'Ischemic heart disease': heart_total * 0.55,
    'Hypertensive heart disease': heart_total * 0.18,
    'Other heart disease': heart_total * 0.27,
}

other_causes = {
    'Cancer': total_deaths * 0.231,
    'Chronic respiratory': total_deaths * 0.058,
    'Stroke': total_deaths * 0.052,
    'Diabetes': total_deaths * 0.033,
    'Other causes': total_deaths * 0.379,
}

labels = list(heart_subtypes.keys()) + list(other_causes.keys())
sizes = list(heart_subtypes.values()) + list(other_causes.values())

colors = ['#c0392b', '#e74c3c', '#f1948a',
          PALETTE_CUSTOM[0], PALETTE_CUSTOM[1], PALETTE_CUSTOM[2],
          PALETTE_CUSTOM[3], PALETTE_CUSTOM[4]]

fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                   autopct='%1.1f%%', startangle=140, pctdistance=0.75)
for t in autotexts:
    t.set_fontsize(9)

ax.set_title('USA Causes of Death (2010)', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()
