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

fig = px.choropleth(
    allages,
    locations="iso_alpha",
    color="death_rate",
    hover_name="country",
    color_continuous_scale="YlGn",
    range_color=(200, 2000),
    title="All-Cause Mortality Rate per 100,000 by Country (2010)",
    labels={"death_rate": "Death Rate\nper 100k"},
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