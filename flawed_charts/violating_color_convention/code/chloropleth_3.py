import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Carbon Dioxide_Emission_Estimates.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})

series = 'Emissions per capita (Metric tons of carbon dioxide)'
latest = df[df['Series'] == series]
latest_year = int(latest['Year'].max())
latest = latest[latest['Year'] == latest_year][['Country', 'Value']].copy()
latest = latest.rename(columns={'Value': 'per_capita'})
latest['per_capita'] = pd.to_numeric(latest['per_capita'], errors='coerce')
latest = latest.dropna(subset=['per_capita'])

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='per_capita',
    hover_name='Country',
    color_continuous_scale=[[0, 'darkred'], [0.2, 'red'], [0.4, 'orange'], [0.6, 'yellow'], [0.8, 'lightyellow'], [1.0, 'white']],
    range_color=(0, 25),
    title=f'CO2 Emissions per Capita by Country ({latest_year})',
    labels={'per_capita': 'tCO₂ per person'},
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