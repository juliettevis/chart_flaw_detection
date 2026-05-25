import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Intentional_homicides_and_other_crimes.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

def latest(series_name, col):
    s = df[df['Series'] == series_name].sort_values('Year')
    s = s.groupby('Country', as_index=False).tail(1)[['Country', 'Value']]
    return s.rename(columns={'Value': col}).dropna()

homicide = latest('Intentional homicide rates per 100,000', 'homicide')
assault = latest('Assault rate per 100,000 population', 'assault')
merged = homicide.merge(assault, on='Country', how='inner')
merged = merged[(merged['homicide'] <= 80) & (merged['assault'] <= 2000)]

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(merged['assault'], merged['homicide'], color=PALETTE_WONG[6],
           alpha=0.6, s=40, edgecolors='none')

x = merged['assault'].values
y = merged['homicide'].values
coeffs = np.polyfit(x, y, 1)
poly = np.poly1d(coeffs)
x_line = np.linspace(x.min(), x.max(), 300)
ax.plot(x_line, poly(x_line), color='steelblue', linewidth=2.5, solid_capstyle='round')

ax.set_title('Homicide Rate vs. Assault Rate (by country)',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Assault rate (per 100,000)', fontsize=12)
ax.set_ylabel('Homicide rate (per 100,000)', fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()