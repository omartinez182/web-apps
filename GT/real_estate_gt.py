#Load libraries
import plotly.express as px
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import base64

#Load dataset
DATA_URL = ("https://raw.githubusercontent.com/omartinez182/web-apps/master/GT/Scrape_Sale_01-01-2021.csv")

#Create initial titles/subtitles
st.title("Real Estate Analysis Guatemala City")
st.markdown("Esta aplicación permite analizar la distribución de precios de propiedades en venta en la Área Metropolitana de la Ciudad de Guatemala. 🇬🇹 🏘️")
st.markdown("Además de las visualizaciones, también es posible desplegar y descargar la data cruda al final de la página.")
st.markdown("<small> Built by Omar Eduardo Martinez </small>", unsafe_allow_html=True)
st.markdown("<small> Data Scraped from the Web </small>", unsafe_allow_html=True)


@st.cache(persist=True)#We use this to cache the info and not load the data every time we scroll up/down
#Function to perform some transformation in the dataframe
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data = data.drop(['Unnamed: 0'], axis=1)
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    return data

#Load 1,0000 rows of data
data = load_data(10000)
data_scatter = data.copy()

st.header("Selecciona la Zona de interes")
#Create a slider to select the zone
selected_zone = st.selectbox("Seleccionar Zona", data['Zone'].unique(), key='zone_box', index=1) #Add a dropdown element
data = data[data['Zone'] == selected_zone]
#Print the average price for the selection & the number of observations available
st.write("El precio medio por m² en", selected_zone, "es de: ", round(data['Price_m2_USD'].median(),2), "US$. Este calculo fue realizado en base a", data.shape[0],"propiedades." )


st.header("Filtra Propiedades dependiendo del # de habitaciones")
#Create a slider to select the number of bedrooms
how_many_bedrooms = st.slider("Selecciona el # de habitaciones", 0, 10, value=3) #Add a slider element
#Create a map based on a query to the dataframe
st.map(data.query("Bedrooms == @how_many_bedrooms")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider
#Filter 
data_bedrooms = data[data['Bedrooms'] == how_many_bedrooms]
#Print the average price for the selection of both zone and # of bedrooms
st.write("El precio medio por m² para", selected_zone, ", en propiedades con", how_many_bedrooms, "habitaciones, es de: ",round(data_bedrooms['Price_m2_USD'].median(),2), "US$. Este calculo fue realizado en base a", data_bedrooms.shape[0],"propiedades.")
#Disclaimer
#st.markdown('<small> *"Precio medio" se refiere a la', '<a href="https://es.wikipedia.org/wiki/Mediana_(estad%C3%ADstica)#:~:text=En%20el%20%C3%A1mbito%20de%20la,Se%20le%20denota%20mediana."> mediana </a>', '(estadística). </small>', unsafe_allow_html=True)
# not centered
st.markdown(
    """<small> *Precio medio se refiere a la <a href="https://es.wikipedia.org/wiki/Mediana_(estad%C3%ADstica)#:~:text=En%20el%20%C3%A1mbito%20de%20la,Se%20le%20denota%20mediana." target="_blank"> mediana (estadística)</a>. </small>""", unsafe_allow_html=True,
)

st.subheader("Propiedades by Precio por m²")
#Explanation
st.write("Este mapa representa la distribución de las propiedades disponibles en", selected_zone, ". La altura y el color de las barras representan el precio en US$ por m².")

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


st.subheader("Propiedades by Superficie Total")
#Explanation
st.write("Este mapa representa la distribución de las propiedades disponibles en", selected_zone, ". La altura y el color de las barras representan la superficie total de las propiedades en m².")

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


#Disclaimer
st.markdown("<small> *No todas las propiedades son desplegadas en el mapa. Debido a la forma en que se recolectan los datos, la latitud y longitud pueden ser un área general, por consiguiente, habrá un traslape en ciertos puntos. No obstante, el número de propiedades analizadas desplegado es preciso. </small>", unsafe_allow_html=True)


#Create a scatter plot with the relationship between zone and price
st.subheader("Relación entre Precio ($US) y Superficie (m²) ")

#Create a slider to select the zone
selected_zone_scatter = st.selectbox("Seleccionar Zona", data_scatter['Zone'].unique(), key='zone_box_scatter', index=1) #Add a dropdown element
data_scatter = data_scatter[data_scatter['Zone'] == selected_zone_scatter]

#Create scatter plot (filtered by zone)
fig = px.scatter(data_scatter, x='Surface', y='Price_USD', trendline="ols", color='Price_m2_USD',
                labels=dict(Surface="Surface in (m²)", Price_USD="Price in (US$)", Price_m2_USD="Price by m²"))
st.write(fig) #write the figure in the web app


#Review the raw data (dataframe) in the app
if st.checkbox('Mostrar Data', False): #Creates a checkbox to show/hide the data
    st.subheader('Data Cruda')
    st.write(data)

#Allow users to download the data
# Credit to: https://discuss.streamlit.io/t/how-to-set-file-download-function/2141
def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="real_estate_data.csv">Download CSV file</a>'

st.markdown(get_table_download_link(data), unsafe_allow_html=True)
