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

parliament_sizes = {
    'China': 2980, 'India': 543, 'United States of America': 435, 'Indonesia': 575,
    'Brazil': 513, 'Pakistan': 336, 'Bangladesh': 350, 'Nigeria': 360,
    'Mexico': 500, 'Japan': 465, 'Ethiopia': 547, 'Philippines': 316,
    'Germany': 736, 'United Kingdom': 650, 'France': 577, 'Italy': 400,
    'South Africa': 400, 'Republic of Korea': 300, 'Spain': 350, 'Canada': 338,
    'Australia': 151, 'Netherlands': 150, 'Sweden': 349, 'Norway': 169,
    'Finland': 200, 'Denmark': 179, 'New Zealand': 120, 'Argentina': 257,
    'Colombia': 188, 'Peru': 130, 'Chile': 155, 'Ecuador': 137,
    'Russian Federation': 450, 'Turkey': 600, 'Iran (Islamic Republic of)': 290,
    'Egypt': 596, 'Thailand': 500, 'Viet Nam': 500, 'Kenya': 349,
    'United Republic of Tanzania': 393, 'Uganda': 529, 'Ghana': 275,
    'Rwanda': 80, 'Cuba': 474, 'Bolivia (Plurinational State of)': 130,
    'Nicaragua': 91, 'Costa Rica': 57, 'Iceland': 63, 'Nepal': 275,
    'Sri Lanka': 225, 'Myanmar': 440, 'Afghanistan': 250, 'Iraq': 329,
    'Saudi Arabia': 150, 'Israel': 120, 'Poland': 460, 'Ukraine': 450,
    'Romania': 330, 'Czechia': 200, 'Hungary': 199, 'Portugal': 230,
    'Greece': 300, 'Belgium': 150, 'Switzerland': 200, 'Austria': 183,
    'Ireland': 160, 'Singapore': 104, 'Malaysia': 222, 'Cambodia': 125,
}

default_size = 150

latest['seats'] = latest.apply(
    lambda row: round((row['pct'] / 100.0) * parliament_sizes.get(row['Country'], default_size)),
    axis=1
)

fig = px.choropleth(
    latest,
    locations='Country',
    locationmode='country names',
    color='seats',
    hover_name='Country',
    color_continuous_scale='Purples',
    title='Seats Held by Women in National Parliament',
    labels={'seats': 'Seats'},
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