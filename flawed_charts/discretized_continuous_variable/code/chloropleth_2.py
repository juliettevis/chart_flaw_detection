import argparse
import sys
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'mortality.csv')
df = pd.read_csv(data_path)
df["Death Rate Per 100,000"] = df["Death Rate Per 100,000"].str.replace(",", "").astype(float)

allages = df[(df["Year"] == 2010) & (df["Age Group"] == "All ages") & (df["Sex"] == "Both")][[
    "Country Code", "Country Name", "Death Rate Per 100,000"
]].copy()
allages.columns = ["iso_alpha", "country", "death_rate"]

# Create categorical bins with boundaries that exaggerate differences
bins = [0, 500, 750, 1000, 1500, float('inf')]
labels = ['Low', 'Moderate', 'High', 'Very High', 'Extreme']
allages['mortality_category'] = pd.cut(allages['death_rate'], bins=bins, labels=labels)

# Define colors appropriate for mortality data (avoiding green for high mortality)
color_mapping = {
    'Low': '#1f77b4',      # Blue
    'Moderate': '#ff7f0e',  # Orange  
    'High': '#d62728',      # Red
    'Very High': '#8b0000', # Dark red
    'Extreme': '#4b0000'    # Very dark red
}

fig = px.choropleth(
    allages,
    locations="iso_alpha",
    color="mortality_category",
    hover_name="country",
    color_discrete_map=color_mapping,
    category_orders={"mortality_category": labels},
    title="All-Cause Mortality Rate per 100,000 by Country (2010)",
    labels={"mortality_category": "Mortality Level"},
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