import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data')

covid = pd.read_csv(os.path.join(data_dir, 'WHO-COVID-19-global-data.csv'))
covid['Date_reported'] = pd.to_datetime(covid['Date_reported'])
window = covid[covid['Date_reported'].dt.year == 2020]
deaths = window.groupby('Country', as_index=False)['New_deaths'].sum()

pop = pd.read_csv(os.path.join(data_dir, 'Population_Surface_Area_and_Density.csv'),
                  skiprows=1, encoding='latin-1')
pop = pop.rename(columns={'Unnamed: 1': 'Country'})
pop = pop[pop['Series'] == 'Population mid-year estimates (millions)']
pop_latest = pop.sort_values('Year').groupby('Country', as_index=False).tail(1)
pop_latest = pop_latest[['Country', 'Value']].rename(columns={'Value': 'pop_m'})
pop_latest['pop_m'] = pd.to_numeric(pop_latest['pop_m'], errors='coerce')

merged = deaths.merge(pop_latest, on='Country', how='inner').dropna(subset=['pop_m'])
merged['per_100k'] = merged['New_deaths'] / (merged['pop_m'] * 10)

bins = [0, 10, 40, 100, float('inf')]
labels = ['Low (0–10)', 'Medium (10–40)', 'High (40–100)', 'Very High (100+)']
merged['mortality_category'] = pd.cut(merged['per_100k'], bins=bins, labels=labels, include_lowest=True)
merged['mortality_category'] = pd.Categorical(merged['mortality_category'], categories=labels, ordered=True)

color_map = {
    'Low (0–10)': '#ffffb2',
    'Medium (10–40)': '#fd8d3c',
    'High (40–100)': '#e31a1c',
    'Very High (100+)': '#67000d',
}

fig = px.choropleth(
    merged,
    locations='Country',
    locationmode='country names',
    color='mortality_category',
    hover_name='Country',
    color_discrete_map=color_map,
    category_orders={'mortality_category': labels},
    title='COVID-19 New Deaths per 100,000 (2020)',
    labels={'mortality_category': 'Deaths per 100k'},
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