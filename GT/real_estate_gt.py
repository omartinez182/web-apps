#Load libraries
import plotly.express as px
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import base64

#Set title and favicon
st.set_page_config(page_title='Precios de Apartamentos y Casas en la Cuidad Guatemala.', page_icon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/lg/57/flag-for-guatemala_1f1ec-1f1f9.png")

#Load dataset
DATA_URL = ("https://raw.githubusercontent.com/omartinez182/web-apps/master/GT/Scrape_Sale_01-01-2021.csv")

#Create initial titles/subtitles
st.title("Real Estate Analysis Guatemala City")
st.markdown("Esta aplicación permite analizar la distribución de precios de propiedades en venta en la Área Metropolitana de la Ciudad de Guatemala. 🇬🇹 🏘️")
st.markdown('De momento, esta es la única base de datos de acceso abierto y motor de análisis de precios de inmuebles en Guatemala. La aplicación tiene como objetivo apoyar a instituciones gubernamentales, "non-profits", y a todos los guatemaltecos a obtener acceso fácil y gratuito a datos relacionados con el mercado de bienes raíces local. Además, provee análisis estadísticos esenciales para apoyar la toma de decisiones, desde la compra de un nuevo hogar, hasta planificaciones urbanas.')
st.markdown("<small> Built by Omar Eduardo Martinez </small>", unsafe_allow_html=True)
st.markdown("<small> Data Scraped from the Web </br> **Last Update:** 01/01/2021 </small>", unsafe_allow_html=True)


@st.cache(persist=True) #We use this to cache the info and not load the data every time we scroll up/down
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows) #Function to perform some transformation in the dataframe
    data = data.drop(['Unnamed: 0'], axis=1)
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    return data

#Load 10,000 rows of data
data = load_data(10000)
data_tot = data.copy()
data_stat = data.copy()
data_stat2 = data.copy()

st.header("Análisis de Zona")
#Create a dropdown to select the zone
selected_zone = st.selectbox("Seleccionar Zona", data['Zone'].unique(), key='zone_box', index=1) #Add a dropdown element
data = data[data['Zone'] == selected_zone]
median = round(data['Price_USD'].median())
#Print the average price for the selection & the number of observations available
st.write("El precio medio por m² en", selected_zone, "es de: ", round(data['Price_m2_USD'].median(),2), "US$. Este calculo fue realizado en base a", data.shape[0],"propiedades. El precio medio total es de", "$"+str("{:,}".format(median)+"."))

st.text("")
st.subheader("Filtra Propiedades dependiendo del # de habitaciones")
#Create a slider to select the number of bedrooms
how_many_bedrooms = st.slider("Selecciona el # de habitaciones", 0, 10, value=3) #Add a slider element
#Filter 
data_bedrooms = data[data['Bedrooms'] == how_many_bedrooms]
median_bdr = round(data_bedrooms['Price_USD'].median())
#Print the average price for the selection of both zone and # of bedrooms
st.write("El precio medio por m² para", selected_zone, ", en propiedades con", how_many_bedrooms, "habitaciones, es de: ",round(data_bedrooms['Price_m2_USD'].median(),2), "US$. Este calculo fue realizado en base a", data_bedrooms.shape[0],"propiedades. El precio medio total es de", "$"+str("{:,}".format(median_bdr)+"."))
#Create a map based on a query to the dataframe
st.map(data.query("Bedrooms == @how_many_bedrooms")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider
#Disclaimer
st.markdown(
    """<small> *Precio medio se refiere a la <a href="https://es.wikipedia.org/wiki/Mediana_(estad%C3%ADstica)#:~:text=En%20el%20%C3%A1mbito%20de%20la,Se%20le%20denota%20mediana." target="_blank"> mediana (estadística)</a>. </small>""", unsafe_allow_html=True,
)
#Disclaimer
st.markdown("<small> *No todas las propiedades son desplegadas en el mapa. Debido a la forma en que se recolectan los datos, la latitud y longitud pueden ser un área general, por consiguiente, habrá un traslape en ciertos puntos. No obstante, el número de propiedades analizadas desplegado es preciso. </small>", unsafe_allow_html=True)


st.text("")
st.subheader("Propiedades por Precio por m²")
#Explanation
st.write("Este mapa representa la distribución de las propiedades disponibles en", selected_zone, ". La altura y el color de las barras representan el precio en US$ por m².")

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
#Create a 3D map with pydeck
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 12,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data[['Price_m2_USD', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 50,
        extruded = True,
        pickable = False,
        elevation_scale = 1,
        elevation_range = [min(data['Price_m2_USD']),max(data['Price_m2_USD'])],
        auto_highlight = True,
        coverage=1
        ),
    ],
))

#Disclaimer
st.markdown("<small> *Debido a la forma en la que se recolectan los datos para la latitud y longitud, la delimitación de las zonas en el mapa puede no ser precisa en ciertas ocasiones, no obstante, la clasificación de zona de la propiedad como tal, si es precisa, por consiguiente, los cálculos de precios medios y cualquier otra métrica también serán precisos. </small>", unsafe_allow_html=True)


st.text("")
st.header("Promedios por Zona")
#Explanation
st.write("El gráfico de barras se encuentra ordenado según el precio promedio por m² de cada zona. El color de cada barra representa el precio promedio total para cada zona, es decir, el promedio de los precios de lista de cada propiedad.")

#Create a multi-select to select the zone
selected_city = st.multiselect("Seleccionar Ciudad", list(data_tot['City'].unique()), key='city_box', default=["Ciudad de Guatemala"]) #Add a dropdown element
mask_city = data_tot['City'].isin(selected_city) # Mask to filter dataframe
data_tot = data_tot[mask_city]

#Average prices by zone
df_mean = data_tot.groupby('Zone').mean() #Group by zone and calculate averages
df_mean = df_mean[['Bedrooms','Bathrooms','Surface','Price_USD','Price_m2_USD']]
df_mean = df_mean.round()
df_mean = df_mean.sort_values(by='Price_m2_USD')

#Create bar plot for averages by zone
fig_bar = px.bar(df_mean,                   
             x = df_mean.index,                          
             y = 'Price_m2_USD',                         
             color = 'Price_USD',                  
             labels=dict(x="Zona", Price_USD="Precio (Avg.) US$", Price_m2_USD="Promedio de Precio por m² (US$)")
             )
fig_bar.update_xaxes(title='')
#fig_bar.layout.yaxis.title.text = 'Número de Propiedades' #Rename y-axis label
st.plotly_chart(fig_bar, use_container_width=True) #write the figure in the web app and make it responsive


st.text("")
st.text("")
#Create a scatter plot with the relationship between zone and price
st.header("Análisis Estadístico")
st.markdown("Esta sección contiene diferentes análisis estadísticos para la zona seleccionada. La idea es entender mejor la distribución de precios de las propiedades, y a un nivel macro, poder tener una idea de que tan importante es el tamaño de los bienes para predecir su precio total.")

#Create a slider to select the zone
selected_zone_stat = st.selectbox("Seleccionar Zona", data_stat['Zone'].unique(), key='zone_box_stat', index=1) #Add a dropdown element
data_stat = data_stat[data_stat['Zone'] == selected_zone_stat]

st.write("Distribución de precios para propiedades en", selected_zone_stat, ".")

#Create a radio button to select the type of price to analyze
hist_var = st.radio("¿Deseas analizar precios totales (precio de lista) o precios por m²?",('Precios Totales', 'Precios por m²'), key='histogram_radio')

if hist_var == 'Precios Totales':
    hist_x = "Price_USD"
else:
    hist_x = "Price_m2_USD"

#Create histogram for price by m2 (filtered by zone)
fig_hist = px.histogram(data_stat, x=hist_x, labels=dict(Price_USD="Precio en US$", Price_m2_USD="Precio por m² ($US)"))
fig_hist.layout.yaxis.title.text = 'Número de Propiedades' #Rename y-axis label
st.plotly_chart(fig_hist, use_container_width=True) #write the figure in the web app and make it responsive
#Explanation on distinction between mean and median
st.write("Nótese que el centro de masa no es el precio medio (mediana) de", round(data_stat[hist_x].median(),2), "$US, que se reporta en la sección de Análisis de Zona, sino el precio promedio, el cual es de", round(data_stat[hist_x].mean(),2), "$US para", selected_zone_stat, ".")

st.subheader("Relación entre Precio ($US) y Superficie (m²)")
#Create scatter plot (filtered by zone)
fig_scatter = px.scatter(data_stat, x='Surface', y='Price_USD', trendline="ols", color='Price_m2_USD',
                labels=dict(Surface="Superficie en m²", Price_USD="Precio en US$", Price_m2_USD="Precio por m² ($US)"))
st.plotly_chart(fig_scatter, use_container_width=True) #write the figure in the web app and make it responsive

#Get results from the linear regression
results = px.get_trendline_results(fig_scatter)
results_summary = results.px_fit_results.iloc[0].summary()

#Note that tables is a list. The table at index 1 is the "core" table. Additionally, read_html puts dfs in a list, so we want index 0
#Credit to: https://stackoverflow.com/questions/51734180/converting-statsmodels-summary-object-to-pandas-dataframe/52976810
results_as_html = results_summary.tables[0].as_html()
reg_results = pd.read_html(results_as_html, header=None, index_col=0)[0] #Read as df
r_squared = reg_results.loc['Dep. Variable:'][3] #Extract R-Squared
st.write("En función del modelo desplegado en el gráfico de dispersión, se puede notar que para la", selected_zone_stat, ", el","{:.0%}".format(r_squared), "de la varianza en el precio puede ser predicha basándose en la cantidad de m² de la propiedad.")
st.markdown("Cuanto más alto este porcentaje, mayor es la dependencia del precio en función de la superficie. Esto podría indicar que otras variables son menos significativas. Por otra parte, si el porcentaje es bajo, puede ser que otras variables que no están siendo consideradas en este análisis tengan un mayor efecto en el precio, por ejemplo, la plusvalía de la zona, seguridad, proximidad a puntos de interés, etc.")
st.markdown("""Por último, también se sugiere considerar la cantidad de observaciones que son parte del análisis, ya que el tamaño de la muestra también puede afectar el <a href="https://es.wikipedia.org/wiki/Coeficiente_de_determinaci%C3%B3n" target="_blank"> coeficiente de determinación.</a>""", unsafe_allow_html=True)


st.text("")
#Comparison between Zones
st.subheader("Comparación de distribución de precios entre Zonas")
selected_zone_stat2 = st.selectbox("Seleccionar una segunda Zona para realizar la comparación.", data_stat2['Zone'].unique(), key='zone_box_2',index=0) #Add a dropdown element
data_stat2 = data_stat2[data_stat2['Zone'] == selected_zone_stat2]

#Create a radio button to select the type of price to analyze
comp_hist_var = st.radio("¿Deseas analizar precios totales (precio de lista) o precios por m²?",('Precios Totales', 'Precios por m²'), key='comparison_histogram_radio')

if comp_hist_var == 'Precios Totales':
    comp_hist_x = "Price_USD"
    comp_label = "Precio en US$"
else:
    comp_hist_x = "Price_m2_USD"
    comp_label = "Precio por m² ($US)"

# Overlay histogram
compare_hist_df = pd.DataFrame(dict(
    Zonas=np.concatenate(([selected_zone_stat]*len(data_stat[comp_hist_x]), [selected_zone_stat2]*len(data_stat2[comp_hist_x]))), 
    data  =np.concatenate((data_stat[comp_hist_x],data_stat2[comp_hist_x]))
))

fig_compare_hist = px.histogram(compare_hist_df, x="data", color="Zonas", barmode="overlay",
                                labels=dict(data=comp_label))
fig_compare_hist.layout.yaxis.title.text = 'Número de Propiedades'
st.plotly_chart(fig_compare_hist, use_container_width=True) #write the figure in the web app and make it responsive
#Summary
st.write("El precio promedio para", selected_zone_stat, "es de", round(data_stat[comp_hist_x].mean(),2), "$US, mientras que el precio promedio para", selected_zone_stat2, "es de", round(data_stat2[comp_hist_x].mean(),2), "$US.")
st.write("Se recomienda también tomar en cuenta el precio medio debido a que es menos sensible a valores atípicos. El precio medio para", selected_zone_stat, "es de", round(data_stat[comp_hist_x].median(),2), "$US, y para", selected_zone_stat2, "es de", round(data_stat2[comp_hist_x].median(),2), "$US.")


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
    return f'<a href="data:file/csv;base64,{b64}" download="real_estate_data.csv">Descargar CSV</a>'

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
