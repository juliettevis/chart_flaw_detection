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

sub = df[df['Series'] == 'Population aged 60+ years old (percentage)'].copy()
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest = latest[['Country', 'Value']].rename(columns={'Value': 'pct_60plus'})
latest['pct_60plus'] = pd.to_numeric(latest['pct_60plus'], errors='coerce')
latest = latest.dropna(subset=['pct_60plus'])

bins = [0, 8, 15, 22, 100]
labels = ['Low (0–8%)', 'Medium (8–15%)', 'High (15–22%)', 'Very High (22%+)']
latest['age_category'] = pd.cut(latest['pct_60plus'], bins=bins, labels=labels, right=True)
latest['age_category'] = pd.Categorical(latest['age_category'], categories=labels, ordered=True)
latest = latest.dropna(subset=['age_category'])

category_colors = {
    'Low (0–8%)': '#ffffb2',
    'Medium (8–15%)': '#fecc5c',
    'High (15–22%)': '#fd8d3c',
    'Very High (22%+)': '#bd0026',
}

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='age_category',
    hover_name='Country',
    color_discrete_map=category_colors,
    category_orders={'age_category': labels},
    title='Population Aged 60+ (%) by Country',
    labels={'age_category': '% aged 60+'},
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