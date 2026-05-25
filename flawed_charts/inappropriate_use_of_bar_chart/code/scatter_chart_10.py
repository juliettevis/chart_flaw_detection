import argparse, sys, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'base_charts'))
from chart_utils import PALETTE_WONG

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'survey_results_public.csv')
df = pd.read_csv(data_path, usecols=['ConvertedComp', 'YearsCodePro'])
df['YearsCodePro'] = pd.to_numeric(df['YearsCodePro'].replace(
    {'Less than 1 year': 0.5, 'More than 50 years': 50}), errors='coerce')
df = df.dropna(subset=['ConvertedComp', 'YearsCodePro'])
df = df[(df['ConvertedComp'] > 0) & (df['ConvertedComp'] <= 500000) &
        (df['YearsCodePro'] <= 50)]
df = df.sample(n=min(3000, len(df)), random_state=0)

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(df['YearsCodePro'], df['ConvertedComp'], color=PALETTE_WONG[2],
       alpha=0.6, width=0.2, edgecolor='none')
ax.set_title('Developer Compensation vs. Years of Professional Coding',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Years coding professionally', fontsize=12)
ax.set_ylabel('Annual compensation (USD)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linewidth=0.3, alpha=0.7)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig(args.output_path, dpi=300)
plt.close()