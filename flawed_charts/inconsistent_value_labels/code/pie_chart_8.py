import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_IBM

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Population_Surface_Area_and_Density.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1').rename(columns={'Unnamed: 1': 'Country'})
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
country = 'Japan'

def latest_val(series):
    s = df[(df['Country'] == country) & (df['Series'] == series)].dropna(subset=['Value'])
    return s.sort_values('Year').iloc[-1]['Value']

young = latest_val('Population aged 0 to 14 years old (percentage)')
old = latest_val('Population aged 60+ years old (percentage)')
middle = 100 - young - old

labels = ['0–14', '15–59', '60+']
values = [young, middle, old]

fig, ax = plt.subplots(figsize=(10, 6))
wedges, _, autotexts = ax.pie(values, labels=None, autopct='%1.1f%%',
    colors=PALETTE_IBM[:3], startangle=90, textprops={'fontsize': 14})

# Make labels inconsistent: different decimal places, font sizes, and formatting styles
# Slice 0 (young, ~11.2%): show with 0 decimal places, small font
autotexts[0].set_text(f'{young:.0f}%')
autotexts[0].set_fontsize(8)

# Slice 1 (middle, ~52.5%): show with 3 decimal places, large font
autotexts[1].set_text(f'{middle:.3f}%')
autotexts[1].set_fontsize(18)

# Slice 2 (old, ~36.3%): show with 1 decimal place, medium font (original style)
autotexts[2].set_text(f'{old:.1f}%')
autotexts[2].set_fontsize(13)

ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12,
          title='Age bracket')
ax.set_title(f'Population by Age Bracket — {country}',
             fontsize=16, fontweight='bold', pad=16)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()