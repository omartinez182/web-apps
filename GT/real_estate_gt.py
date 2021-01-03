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

st.header("Selecciona de Zona")
#Create a slider to select the zone
selected_zone = st.selectbox("Seleccionar Zona", data['Zone'].unique(), key='zone_box', index=1) #Add a dropdown element
data = data[data['Zone'] == selected_zone]
#Print the average price for the selection & the number of observations available
st.write("El precio medio por m² en", selected_zone, "es de: ", round(data['Price_m2_USD'].median(),2), "US$. Este calculo fue realizado en base a", data.shape[0],"propiedades." )

st.text("")
st.subheader("Filtra Propiedades dependiendo del # de habitaciones")
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


st.text("")
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


st.text("")
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


st.text("")
st.text("")
#Create a scatter plot with the relationship between zone and price
st.header("Análisis de Estadístico")
st.subheader("Relación entre Precio ($US) y Superficie (m²)")

#Create a slider to select the zone
selected_zone_scatter = st.selectbox("Seleccionar Zona", data_scatter['Zone'].unique(), key='zone_box_scatter', index=1) #Add a dropdown element
data_scatter = data_scatter[data_scatter['Zone'] == selected_zone_scatter]

#Create scatter plot (filtered by zone)
fig = px.scatter(data_scatter, x='Surface', y='Price_USD', trendline="ols", color='Price_m2_USD',
                labels=dict(Surface="Surface in (m²)", Price_USD="Price in (US$)", Price_m2_USD="Price by m²"))
st.write(fig) #write the figure in the web app

#Get results from the linear regression
results = px.get_trendline_results(fig)
results_summary = results.px_fit_results.iloc[0].summary()

#Note that tables is a list. The table at index 1 is the "core" table. Additionally, read_html puts dfs in a list, so we want index 0
#Credit to: https://stackoverflow.com/questions/51734180/converting-statsmodels-summary-object-to-pandas-dataframe/52976810
results_as_html = results_summary.tables[0].as_html()
reg_results = pd.read_html(results_as_html, header=None, index_col=0)[0] #Read as df
r_squared = reg_results.loc['Dep. Variable:'][3] #Extract R-Squared
st.write("En función del modelo desplegado en el gráfico de dispersión, se puede notar que para la", selected_zone_scatter, " el","{:.0%}".format(r_squared), "de la varianza en el precio puede ser predicha basándose en el valor la superficie.")
st.markdown("Cuanto más alto este porcentaje, mayor es la dependencia del precio en función de la superficie. Esto podría indicar que otras variables son menos significativas. Si el porcentaje es bajo, puede ser que otras variables que no están siendo consideradas en este análisis, tengan un mayor efecto en el precio, por ejemplo, la plusvalía de la zona, seguridad, proximidad a puntos de interés, etc.")
st.markdown("Por último, también se sugiere considerar la cantidad de observaciones que son partes del análisis, ya que el tamaño de la muestra también puede afectar el coeficiente de determinación.")

st.text("")
st.text("")
st.subheader("Data Cruda")
st.markdown('Al hacer clic en la caja "Mostrar Data", se desplegara la tabla con los datos para la zona seleccionada. Además, es posible descargar la tabla en formato CSV haciendo clic en el enlace que se encuentra debajo de la tabla.')
#Review the raw data (dataframe) in the app
if st.checkbox('Mostrar Data', False): #Creates a checkbox to show/hide the data
    st.write(data)

#Allow users to download the data
#Credit to: https://discuss.streamlit.io/t/how-to-set-file-download-function/2141
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


st.text("")
st.text("")
st.text("")
#Feedback and suggestions
st.markdown('Para cualquier sugerencia o reportar errores, por favor contáctame <a href="mailto:omartinez1821992@gmail.com">aquí</a>.', unsafe_allow_html=True)

#Hide hamburger menu & footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
