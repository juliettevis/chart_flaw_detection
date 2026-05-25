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

sub = df[df['Series'] == 'Population mid-year estimates (millions)'].copy()
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_year = int(latest['Year'].max())
latest = latest[['Country', 'Value']].rename(columns={'Value': 'population'})
latest['population'] = latest['population'].astype(str).str.replace(',', '').str.strip()
latest['population'] = pd.to_numeric(latest['population'], errors='coerce')
latest = latest.dropna(subset=['population'])
regions = ['Total, all countries or areas', 'Africa', 'Asia', 'Europe', 'Americas',
           'Oceania', 'Northern America', 'South America', 'Central America',
           'Eastern Africa', 'Middle Africa', 'Northern Africa', 'Southern Africa',
           'Western Africa', 'Caribbean', 'Eastern Asia', 'South-central Asia',
           'South-eastern Asia', 'Southern Asia', 'Western Asia', 'Eastern Europe',
           'Northern Europe', 'Southern Europe', 'Western Europe',
           'Australia and New Zealand', 'Melanesia', 'Micronesia', 'Polynesia',
           'Sub-Saharan Africa', 'Latin America & the Caribbean']
latest = latest[~latest['Country'].isin(regions)]
latest = latest[~latest['Country'].str.contains('LDC|LLDC|SIDS|income', case=False, na=False)]

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='population',
    hover_name='Country',
    color_continuous_scale='Viridis',
    title=f'Total Population by Country ({latest_year})',
    labels={'population': 'Population (millions)'},
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