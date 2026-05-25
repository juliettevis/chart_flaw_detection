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

fig = px.choropleth(
    data_2013,
    locations="iso_alpha",
    color="prevalence",
    hover_name="country",
    color_continuous_scale="YlOrRd_r",
    range_color=(0, 800),
    title="TB Prevalence per 100,000 Population by Country (2013)",
    labels={"prevalence": "Prevalence\nper 100k"},
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