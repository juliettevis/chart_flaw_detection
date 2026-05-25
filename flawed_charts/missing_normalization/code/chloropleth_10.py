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

sub = df[df['Series'] == 'Population mid-year estimates for females (millions)'].copy()
sub['Value'] = sub['Value'].astype(str).str.replace(',', '', regex=False)
sub['Value'] = pd.to_numeric(sub['Value'], errors='coerce')
sub = sub.dropna(subset=['Value'])
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_year = int(latest['Year'].max())
latest = latest[['Country', 'Value']].copy()
latest = latest.rename(columns={'Value': 'female_pop'})

aggregates = ["Total, all countries or areas", "Africa", "Northern Africa", "Sub-Saharan Africa",
              "Eastern Africa", "Middle Africa", "Southern Africa", "Western Africa",
              "Americas", "Northern America", "Latin America and the Caribbean",
              "Caribbean", "Central America", "South America",
              "Asia", "Central Asia", "Eastern Asia", "South-eastern Asia",
              "Southern Asia", "Western Asia", "Europe", "Eastern Europe",
              "Northern Europe", "Southern Europe", "Western Europe",
              "Oceania", "Australia and New Zealand", "Melanesia", "Micronesia", "Polynesia"]
latest = latest[~latest['Country'].isin(aggregates)]

colorscale = [
    (0.0, 'rgb(20,50,140)'),
    (0.5, 'rgb(200,180,220)'),
    (1.0, 'rgb(175,25,105)'),
]

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='female_pop',
    hover_name='Country',
    color_continuous_scale=colorscale,
    title=f'Female Population by Country ({latest_year})',
    labels={'female_pop': 'Female pop (millions)'},
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