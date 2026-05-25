import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Intentional_homicides_and_other_crimes.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})

series = 'Intentional homicide rates per 100,000'
sub = df[df['Series'] == series].copy()
sub = sub[sub['Country'].notna() & (sub['Country'].str.strip() != '')]
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_year = int(latest['Year'].max())
latest = latest[['Country', 'Value']].rename(columns={'Value': 'rate'})
latest['rate'] = pd.to_numeric(latest['rate'], errors='coerce')
latest = latest.dropna(subset=['rate'])

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='rate',
    hover_name='Country',
    color_continuous_scale='Greens',
    range_color=(0, 40),
    title=f'Intentional Homicide Rate by Country ({latest_year})',
    labels={'rate': 'Homicides per 100,000'},
)

fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True, coastlinecolor='lightgray',
             projection_type='natural earth'),
    title_font_size=16,
    title_x=0.5,
    margin=dict(l=10, r=10, t=50, b=10),
    width=1000,
    height=550,
)

fig.write_image(args.output_path, scale=2)