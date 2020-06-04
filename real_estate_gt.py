from pandas import json_normalize
import plotly.express as px
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np


DATA_URL = ("Scrape_20202.csv")

st.title("Real Estate Overview Guatemala City")
st.markdown("Dashboard to Analyze Properties for Sale in Guatemala City 🇬🇹 🏘️")
st.markdown("Built by Eduardo Martinez")
st.markdown("Data Scraped from the Web")


@st.cache(persist=True)#We use this to cache the info and not load the data every time we scroll up/down
#Function to perform some transformation in the dataframe
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    return data

#Load 1,0000 rows of data
data = load_data(10000)


st.header("Filter Properties by # of Beedrooms")
#Create a slider to select the number of people
how_many_bedrooms = st.slider("Select # of Beedrooms", 0, 10) #Add a slider element
#Create a map based on a query to the dataframe
st.map(data.query("number_of_bedrooms >= @how_many_bedrooms")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider


st.subheader("Property Prices by Location")
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
        data = data[['price_usd', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 6,
        elevation_range = [0,500],
        auto_highlight = True,
        ),
    ],
))


st.subheader("Property Prices by Squared Meters (Total Surface)")
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
        data = data[['m2', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 6,
        elevation_range = [0,500],
        auto_highlight = True,
        ),
    ],
))


#Review the raw data (dataframe) in the app
if st.checkbox('Show Raw Data', False): #Creates a checkbox to show/hide the data
    st.subheader('Raw Data')
    st.write(data)
