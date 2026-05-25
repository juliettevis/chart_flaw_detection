import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Intentional_homicides_and_other_crimes.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
sub = df[df['Series'] == 'Intentional homicide rates per 100,000']
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1).dropna(subset=['Value'])
top = latest.nlargest(15, 'Value').sort_values('Value', ascending=True)

arbitrary_order = [
    'Honduras',
    'Turks and Caicos Islands',
    'Saint Lucia',
    'Belize',
    'Jamaica',
    'Lesotho',
    'South Africa',
    'Anguilla',
    'Trinidad and Tobago',
    'Ecuador',
    'Dominica',
    'Haiti',
    'Bahamas (The)',
    'United States Virgin Islands',
    'Saint Vincent & Grenadines',
]

top = top.set_index('Country').loc[arbitrary_order].reset_index()

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(top['Country'], top['Value'], color=PALETTE_WONG[6])
ax.set_title('Top 15 Countries — Intentional Homicide Rate',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Homicides per 100,000', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.xaxis.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()