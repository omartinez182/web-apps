from pandas import json_normalize
from sodapy import Socrata
import plotly.express as px
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import requests
import json

#Query the API
client = Socrata("data.cityofnewyork.us", None)

# dictionaries by sodapy.
results = client.get("h9gi-nx95", limit=20000)

# Convert to pandas DataFrame
DATA_URL = pd.DataFrame.from_records(results)


st.title("Motor Vehicle Collisions in NYC")
st.markdown("Dashboard to Analyze Collisions in NYC 🗽")
st.markdown("Built by Eduardo Martinez")
st.markdown("Data: NYC Open Data API")

#Function to perform some transformacion in the dataframe
@st.cache(persist = True, allow_output_mutation = True) #We use this to cache the info and not load the data every time we scroll up/down
def load_data(df, nrows):
    df['crash_date'] = pd.to_datetime(df['crash_date']) #Parse dates
    df['crash_time'] = pd.to_datetime(df['crash_time'], format = '%H:%M') #Parse time
    data = df
    data.dropna(subset=['latitude', 'longitude'], inplace = True) #Drop missing values (NAs)
    data['number_of_persons_injured'] = data['number_of_persons_injured'].astype(int)
    data['number_of_pedestrians_injured'] = data['number_of_pedestrians_injured'].astype(int)
    data['number_of_cyclist_injured'] = data['number_of_cyclist_injured'].astype(int)
    data['number_of_motorist_injured'] = data['number_of_motorist_injured'].astype(int)
    data['latitude'] = data['latitude'].astype(float)
    data['longitude'] = data['longitude'].astype(float)
    return data

#Load 100,000 rows
data = load_data(DATA_URL,20000)
original_data = data

st.header("Where are the most people injured in NYC?")
#Create a slider to select the number of people
injured_people = st.slider("Number of Persons Injured in Vehicle Collisions", 0, 19) #Add a slider element
#Create a map based on a query to the dataframe
st.map(data.query("number_of_persons_injured >= @injured_people")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider


st.header("How many collisions occur at any given time of the day?")
#Creaate a slider to select any hour
hour = st.slider("Select an Hour", 0, 23)
data = data[data['crash_time'].dt.hour == hour]
data['crash_time_hour'] = data['crash_time'].dt.hour


st.markdown("Vehicle Collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
#Create a 3D map with pydeck
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data[['crash_time_hour', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0,1000],
        ),
    ],
))


#Create a histogram with the number of crashes by minute
st.subheader("Breakdown by Minute between %i:00 and %i:00" % (hour, (hour +1) % 24))
filtered = data[
    (data['crash_time_hour'] >= hour) & (data['crash_time_hour'] < (hour +1))
]
#Create the histogram (filtered)
hist = np.histogram(filtered['crash_time'].dt.minute, bins = 60, range = (0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist}) #Convert histogram data to a dataframe to pass to plotly
#Create the plotly figure (needs to get passed a dataframe)
fig = px.bar(chart_data, x='minute', y='crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig) #write the figure in the web app


#Create dropdown filters for type of individual involved and Streets
st.header("Top 5 Dangerous Streets by Type")
select = st.selectbox('Affected Type of Individual', ['Pedestrians', 'Cyclists', 'Motorists'])
#Pedestrians injured by on_street_name
if select == 'Pedestrians':
    st.write(original_data.query('number_of_pedestrians_injured >= 1')[['on_street_name', 'number_of_pedestrians_injured']].sort_values(by = ['number_of_pedestrians_injured'], ascending = False).dropna(how = 'any')[:5])
#Cyclists injured by on_street_name
elif select == 'Cyclists':
    st.write(original_data.query('number_of_cyclist_injured >= 1')[['on_street_name', 'number_of_cyclist_injured']].sort_values(by = ['number_of_cyclist_injured'], ascending = False).dropna(how = 'any')[:5])
#Motorist injured by on_street_name
else:
    st.write(original_data.query('number_of_motorist_injured >= 1')[['on_street_name', 'number_of_motorist_injured']].sort_values(by = ['number_of_motorist_injured'], ascending = False).dropna(how = 'any')[:5])


#Review the raw data (dataframe) in the app
if st.checkbox('Show Raw Data', False): #Creates a checkbox to show/hide the data
    st.subheader('Raw Data')
    st.write(data)
