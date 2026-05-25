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

bins = [0, 3, 7, 12, 100]
labels = ['Low (0–3)', 'Medium (3–7)', 'High (7–12)', 'Very High (12+)']
latest['emission_category'] = pd.cut(latest['per_capita'], bins=bins, labels=labels, right=True)
latest['emission_category'] = pd.Categorical(latest['emission_category'], categories=labels, ordered=True)
latest = latest.dropna(subset=['emission_category'])

color_map = {
    'Low (0–3)': '#ffffb2',
    'Medium (3–7)': '#fecc5c',
    'High (7–12)': '#f03b20',
    'Very High (12+)': '#7b0000',
}

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='emission_category',
    hover_name='Country',
    color_discrete_map=color_map,
    category_orders={'emission_category': labels},
    title=f'CO2 Emissions per Capita by Country ({latest_year})',
    labels={'emission_category': 'tCO₂ per person'},
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