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
df["Number of Deaths"] = df["Number of Deaths"].str.replace(",", "").astype(float)

allages = df[(df["Year"] == 2010) & (df["Age Group"] == "All ages") & (df["Sex"] == "Both")][[
    "Country Code", "Country Name", "Number of Deaths"
]].copy()
allages.columns = ["iso_alpha", "country", "total_deaths"]

fig = px.choropleth(
    allages,
    locations="iso_alpha",
    color="total_deaths",
    hover_name="country",
    color_continuous_scale="YlOrRd",
    range_color=(0, 15000000),
    title="All-Cause Mortality by Country (2010)",
    labels={"total_deaths": "Total Deaths"},
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