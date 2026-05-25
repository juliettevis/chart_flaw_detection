import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'electricity_production_from_renewable_sources_excluding_hydroelectric.csv')
df = pd.read_csv(data_path, skiprows=3)

year = '2021'
df[year] = pd.to_numeric(df[year], errors='coerce')
plot_df = df[['Country Name', year]].dropna()
plot_df = plot_df[plot_df[year] >= 0]
plot_df = plot_df.rename(columns={year: 'pct'})

fig = px.choropleth(
    plot_df,
    locations='Country Name',
    locationmode='country names',
    color='pct',
    hover_name='Country Name',
    color_continuous_scale='Reds',
    title='Electricity from Renewables (excl. hydro), % of total (2021)',
    labels={'pct': '% of total'},
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