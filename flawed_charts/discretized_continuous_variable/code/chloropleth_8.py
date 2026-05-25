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

bins = [0, 15, 25, 35, 100]
labels = ['Low (0–15%)', 'Medium (15–25%)', 'High (25–35%)', 'Very High (35%+)']
latest['pct_category'] = pd.cut(latest['pct'], bins=bins, labels=labels, include_lowest=True)
latest['pct_category'] = pd.Categorical(latest['pct_category'], categories=labels, ordered=True)

category_colors = {
    'Low (0–15%)': '#f7c6c7',
    'Medium (15–25%)': '#c084c8',
    'High (25–35%)': '#7b2d8b',
    'Very High (35%+)': '#2d004b',
}

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='pct_category',
    hover_name='Country',
    color_discrete_map=category_colors,
    category_orders={'pct_category': labels},
    title='Seats Held by Women in National Parliament (%)',
    labels={'pct_category': 'Representation Level'},
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