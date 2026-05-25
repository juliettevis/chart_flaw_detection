import argparse
import sys
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'tuberculosis.csv')
df = pd.read_csv(data_path)

data_2013 = df[df["Year"] == 2013][[
    "ISO 3-character country/territory code",
    "Country or territory name",
    "Estimated prevalence of TB (all forms) per 100 000 population"
]].dropna().copy()
data_2013.columns = ["iso_alpha", "country", "prevalence"]

# Create categories with boundaries that exaggerate small differences
data_2013['prevalence_category'] = pd.cut(
    data_2013['prevalence'],
    bins=[0, 50, 100, 250, 400, 800],
    labels=['Low', 'Moderate', 'High', 'Very High', 'Critical'],
    include_lowest=True
)

# Define colors that are appropriate for negative health outcomes
color_map = {
    'Low': '#3182bd',      # Blue
    'Moderate': '#9ecae1', # Light blue
    'High': '#fdae6b',     # Light orange
    'Very High': '#fd8d3c', # Orange
    'Critical': '#d94701'   # Dark orange
}

fig = px.choropleth(
    data_2013,
    locations="iso_alpha",
    color="prevalence_category",
    hover_name="country",
    color_discrete_map=color_map,
    category_orders={"prevalence_category": ['Low', 'Moderate', 'High', 'Very High', 'Critical']},
    title="TB Prevalence per 100,000 Population by Country (2013)",
    labels={"prevalence_category": "Prevalence\nCategory"},
)

fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True, coastlinecolor="lightgray",
             projection_type="natural earth"),
    title_font_size=16,
    title_x=0.5,
    margin=dict(l=10, r=10, t=50, b=10),
    width=1000,
    height=550,
)

fig.write_image(args.output_path, scale=2)