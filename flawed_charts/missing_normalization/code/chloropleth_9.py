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

sub_pct = df[df['Series'] == 'Population aged 60+ years old (percentage)'].copy()
latest_pct = sub_pct.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_pct = latest_pct[['Country', 'Year', 'Value']].rename(columns={'Value': 'pct_60plus'})
latest_pct['pct_60plus'] = pd.to_numeric(latest_pct['pct_60plus'], errors='coerce')
latest_pct = latest_pct.dropna(subset=['pct_60plus'])

sub_pop = df[df['Series'] == 'Population mid-year estimates (millions)'].copy()
sub_pop['Value'] = sub_pop['Value'].astype(str).str.replace(',', '', regex=False)
sub_pop['Value'] = pd.to_numeric(sub_pop['Value'], errors='coerce')
latest_pop = sub_pop.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_pop = latest_pop[['Country', 'Value']].rename(columns={'Value': 'pop_millions'})
latest_pop = latest_pop.dropna(subset=['pop_millions'])

regions = ['Total, all countries or areas', 'Africa', 'Asia', 'Europe', 'Americas',
           'Oceania', 'Northern America', 'South America', 'Central America',
           'Eastern Africa', 'Middle Africa', 'Northern Africa', 'Southern Africa',
           'Western Africa', 'Caribbean', 'Eastern Asia', 'South-central Asia',
           'South-eastern Asia', 'Southern Asia', 'Western Asia', 'Eastern Europe',
           'Northern Europe', 'Southern Europe', 'Western Europe',
           'Australia and New Zealand', 'Melanesia', 'Micronesia', 'Polynesia',
           'Sub-Saharan Africa', 'Latin America & the Caribbean']
latest_pct = latest_pct[~latest_pct['Country'].isin(regions)]
latest_pct = latest_pct[~latest_pct['Country'].str.contains('LDC|LLDC|SIDS|income', case=False, na=False)]
latest_pop = latest_pop[~latest_pop['Country'].isin(regions)]
latest_pop = latest_pop[~latest_pop['Country'].str.contains('LDC|LLDC|SIDS|income', case=False, na=False)]

merged = latest_pct.merge(latest_pop, on='Country', how='inner')
merged['abs_60plus'] = merged['pct_60plus'] / 100.0 * merged['pop_millions']

fig = px.choropleth(
    merged,
    locations='Country',
    locationmode='country names',
    color='abs_60plus',
    hover_name='Country',
    color_continuous_scale='Greys',
    title='Population Aged 60+ by Country',
    labels={'abs_60plus': 'Pop 60+ (millions)'},
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