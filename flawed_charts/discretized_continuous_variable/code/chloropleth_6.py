import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Population_Surface_Area_and_Density.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})

sub = df[df['Series'] == 'Population density'].copy()
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_year = int(latest['Year'].max())
latest = latest[['Country', 'Value']].rename(columns={'Value': 'density'})
latest['density'] = pd.to_numeric(latest['density'], errors='coerce')
latest = latest.dropna(subset=['density'])

bins = [0, 25, 100, 200, float('inf')]
labels = ['Low', 'Medium', 'High', 'Very High']
latest['density_cat'] = pd.cut(latest['density'], bins=bins, labels=labels, right=True)
latest['density_cat'] = pd.Categorical(latest['density_cat'], categories=labels, ordered=True)

color_map = {
    'Low': '#d1e5f0',
    'Medium': '#4393c3',
    'High': '#d6604d',
    'Very High': '#8e0152',
}

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='density_cat',
    hover_name='Country',
    color_discrete_map=color_map,
    category_orders={'density_cat': labels},
    title=f'Population Density by Country ({latest_year})',
    labels={'density_cat': 'Population density per km²'},
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