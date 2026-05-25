import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Seats_held_by_women_in_Parliament.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})

latest = df.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest = latest[['Country', 'Value']].rename(columns={'Value': 'pct'})
latest['pct'] = pd.to_numeric(latest['pct'], errors='coerce')
latest = latest.dropna()

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='pct',
    hover_name='Country',
    color_continuous_scale='Purples_r',
    title='Seats Held by Women in National Parliament (%)',
    labels={'pct': '%'},
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