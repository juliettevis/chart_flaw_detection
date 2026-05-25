import argparse
import os
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

data_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data',
                         'Intentional_homicides_and_other_crimes.csv')
df = pd.read_csv(data_path, skiprows=1, encoding='latin-1')
df = df.rename(columns={'Unnamed: 1': 'Country'})

series = 'Intentional homicide rates per 100,000'
sub = df[df['Series'] == series].copy()
sub = sub[sub['Country'].notna() & (sub['Country'].str.strip() != '')]
latest = sub.sort_values('Year').groupby('Country', as_index=False).tail(1)
latest_year = int(latest['Year'].max())
latest = latest[['Country', 'Value']].rename(columns={'Value': 'rate'})
latest['rate'] = pd.to_numeric(latest['rate'], errors='coerce')
latest = latest.dropna(subset=['rate'])

population_estimates = {
    'China': 1425000000, 'India': 1428000000, 'United States of America': 335000000,
    'Indonesia': 277000000, 'Pakistan': 230000000, 'Nigeria': 223000000,
    'Brazil': 216000000, 'Bangladesh': 173000000, 'Russia': 144000000,
    'Russian Federation': 144000000, 'Mexico': 128000000, 'Ethiopia': 126000000,
    'Japan': 124000000, 'Philippines': 117000000, 'Egypt': 112000000,
    'Democratic Republic of the Congo': 102000000, 'Viet Nam': 99000000,
    'Germany': 84000000, 'Türkiye': 85000000, 'Turkey': 85000000,
    'Iran (Islamic Republic of)': 88000000, 'Thailand': 72000000,
    'United Kingdom': 68000000, 'France': 66000000, 'Italy': 59000000,
    'South Africa': 60000000, 'Kenya': 55000000, 'Colombia': 52000000,
    'Spain': 48000000, 'Argentina': 46000000, 'Uganda': 48000000,
    'Canada': 39000000, 'Australia': 26000000, 'Venezuela (Bolivarian Republic of)': 28000000,
    'Peru': 34000000, 'Chile': 20000000, 'Ecuador': 18000000,
    'Honduras': 10000000, 'El Salvador': 6500000, 'Jamaica': 3000000,
    'Trinidad and Tobago': 1400000, 'Belize': 400000,
    'Guatemala': 17000000, 'Dominican Republic': 11000000,
    'Costa Rica': 5200000, 'Panama': 4400000, 'Paraguay': 7000000,
    'Bolivia (Plurinational State of)': 12000000, 'Uruguay': 3500000,
    'Nicaragua': 7000000, 'Cuba': 11000000, 'Haiti': 12000000,
    'Mozambique': 33000000, 'United Republic of Tanzania': 65000000,
    'Ghana': 34000000, 'Cameroon': 28000000, 'Angola': 36000000,
    'Lesotho': 2300000, 'Eswatini': 1200000, 'Botswana': 2600000,
    'Namibia': 2600000, 'Rwanda': 14000000, 'Zambia': 20000000,
    'Zimbabwe': 16000000, 'Malawi': 20000000, 'Senegal': 17000000,
    'Nepal': 30000000, 'Sri Lanka': 22000000, 'Myanmar': 55000000,
    'Republic of Korea': 52000000, 'Malaysia': 34000000,
    'New Zealand': 5200000, 'Norway': 5500000, 'Sweden': 10000000,
    'Finland': 5600000, 'Denmark': 5900000, 'Netherlands': 18000000,
    'Belgium': 12000000, 'Switzerland': 9000000, 'Austria': 9000000,
    'Portugal': 10000000, 'Greece': 10000000, 'Czechia': 11000000,
    'Poland': 37000000, 'Romania': 19000000, 'Hungary': 10000000,
    'Ireland': 5100000, 'Lithuania': 2800000, 'Latvia': 1900000,
    'Estonia': 1400000, 'Iceland': 380000, 'Luxembourg': 660000,
}

latest['population'] = latest['Country'].map(population_estimates)
latest['absolute_homicides'] = latest['rate'] * latest['population'] / 100000
latest_with_pop = latest.dropna(subset=['absolute_homicides']).copy()

fig = px.choropleth(
    latest_with_pop,
    locations='Country',
    locationmode='country names',
    color='absolute_homicides',
    hover_name='Country',
    color_continuous_scale='Reds',
    title=f'Total Intentional Homicides by Country ({latest_year})',
    labels={'absolute_homicides': 'Number of homicides'},
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