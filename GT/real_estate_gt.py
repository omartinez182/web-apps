#Load libraries
import plotly.express as px
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

#Load dataset
DATA_URL = ("https://raw.githubusercontent.com/omartinez182/web-apps/master/GT/Scrape_Sale_01-01-2021.csv")

#Create initial titles/subtitles
st.title("Real Estate Analysis Guatemala City")
st.markdown("Esta aplicación te permite analizar los precios de propiedades en venta en la Ciudad de Guatemala. 🇬🇹 🏘️")
st.markdown("Además de las visualizaciones, también puedes encontrar la data cruda al final de la página.")
st.markdown("Built by Omar Eduardo Martinez")
st.markdown("Data Scraped from the Web")


@st.cache(persist=True)#We use this to cache the info and not load the data every time we scroll up/down
#Function to perform some transformation in the dataframe
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    return data

#Load 1,0000 rows of data
data = load_data(10000)

st.header("Selecciona la Zona de interes")
#Create a slider to select the zone
selected_zone = st.selectbox("Seleccionar Zona", data['Zone'].unique(), key='zone_box', index=1) #Add a dropdown element
data = data[data['Zone'] == selected_zone]
#Print the average price for the selection & the number of observations available
st.write("El precio promedio por metro cuadrado en", selected_zone, "es de: ", round(data['Price_m2_USD'].mean(),2), "US$. Este calculo fue realizado en base a", data.shape[0],"propiedades." )


st.header("Filtra Propiedades dependiendo del # de habitaciones")
#Create a slider to select the number of bedrooms
how_many_bedrooms = st.slider("Selecciona el # de habitaciones", 0, 10, value=3) #Add a slider element
#Create a map based on a query to the dataframe
st.map(data.query("Bedrooms == @how_many_bedrooms")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider
#Filter 
data2 = data[data['Bedrooms'] == how_many_bedrooms]
#Print the average price for the selection of both zone and # of bedrooms
st.write("El precio promedio por metro cuadrado para", selected_zone, ", en propiedades con", how_many_bedrooms, "habitaciones, es de: ",round(data2['Price_m2_USD'].mean(),2), "US$")


st.subheader("Precios por Zona/Ubicacion (Precios por Metro Cuadrado)")
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
        data = data[['Price_m2_USD', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 2,
        elevation_range = [min(data['Price_m2_USD']),max(data['Price_m2_USD'])],
        auto_highlight = True,
        ),
    ],
))


st.subheader("Propiedades por Superficie Total")
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
        data = data[['Surface', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 6,
        elevation_range = [min(data['Surface']),max(data['Surface'])],
        auto_highlight = True,
        ),
    ],
))


#Review the raw data (dataframe) in the app
if st.checkbox('Mostrar Data', False): #Creates a checkbox to show/hide the data
    st.subheader('Data Cruda')
    st.write(data)
