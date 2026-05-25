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

sub = df[df['Series'] == 'Sex ratio (males per 100 females)'].copy()
sub['Value'] = pd.to_numeric(sub['Value'], errors='coerce')
sub = sub.dropna(subset=['Value'])
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_year = int(latest['Year'].max())
latest = latest[['Country', 'Value']].copy()
latest['fm_ratio'] = 100.0 / latest['Value']

colorscale = [
    (0.0, 'rgb(175,25,105)'),
    (0.5, 'rgb(200,180,220)'),
    (1.0, 'rgb(20,50,140)'),
]

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='fm_ratio',
    hover_name='Country',
    color_continuous_scale=colorscale,
    color_continuous_midpoint=1.0,
    range_color=(0.85, 1.15),
    title=f'Female-to-Male Population Ratio by Country ({latest_year})',
    labels={'fm_ratio': 'Females per male'},
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