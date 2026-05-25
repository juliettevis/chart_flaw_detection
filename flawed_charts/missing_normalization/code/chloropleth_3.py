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

series = 'Emissions (thousand metric tons of carbon dioxide)'
latest = df[df['Series'] == series]
latest_year = int(latest['Year'].max())
latest = latest[latest['Year'] == latest_year][['Country', 'Value']].copy()
latest = latest.rename(columns={'Value': 'total_emissions'})
latest['total_emissions'] = latest['total_emissions'].astype(str).str.replace(',', '')
latest['total_emissions'] = pd.to_numeric(latest['total_emissions'], errors='coerce')
latest = latest.dropna(subset=['total_emissions'])
latest = latest[~latest['Country'].str.contains('Total|Africa|America|Asia|Europe|Oceania', case=False, na=False)]

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='total_emissions',
    hover_name='Country',
    color_continuous_scale='YlOrRd',
    title=f'Total CO₂ Emissions by Country ({latest_year})',
    labels={'total_emissions': 'tCO₂'},
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