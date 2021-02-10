#Load libraries
import plotly.express as px
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import base64

#Set title and favicon
st.set_page_config(page_title='Precios de Apartamentos y Casas en la Cuidad Guatemala.', page_icon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/lg/57/flag-for-guatemala_1f1ec-1f1f9.png")
st.markdown('<html lang="es"><html translate="no">', unsafe_allow_html=True)

#Load dataset
DATA_URL = ("https://raw.githubusercontent.com/omartinez182/web-apps/master/GT/Scrape_Sale_01-07-2021.csv")

#Create initial titles/subtitles
st.title("Guatemalaviva")
st.write('<html lang="es"><html translate="no">', '<h2> Análisis Inmobiliario </h2>', unsafe_allow_html=True)
st.markdown("Esta aplicación permite analizar la distribución de precios de propiedades en venta en la Área Metropolitana de la Ciudad de Guatemala.")
st.write('<html lang="es"><html translate="no">', 'De momento, esta es la única base de datos de acceso abierto y motor de análisis de precios de inmuebles en Guatemala. La aplicación tiene como objetivo apoyar a instituciones gubernamentales, "non-profits", y todos los guatemaltecos a obtener acceso fácil y gratuito a datos relacionados con el mercado de bienes raíces local. Además, provee análisis estadísticos esenciales para apoyar la toma de decisiones, desde la compra de un nuevo hogar, hasta planificaciones urbanas.', unsafe_allow_html=True)
st.text("")
st.markdown("<small> Datos recolectados de la Web </br> **Ultima Actualización:** 02/09/2021 </small>", unsafe_allow_html=True)

@st.cache(persist=True) #We use this to cache the info and not load the data every time we scroll up/down
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows) #Function to perform some transformation in the dataframe
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    return data

#Load 10,000 rows of data
data = load_data(10000)

#Create a dropdown to select the type of property
selected_type = st.selectbox("Seleccionar Tipo de Propiedad", ['Casas','Apartamentos'], key='property_type_box', index=0) #Add a dropdown element
#Filter depending on the selection
if (selected_type == 'Casas'):
    data = data[data['Tipo'] == 42021]
else:
    data = data[data['Tipo'] == 42020]
#Create copies for other the diffferent sections
data_tot = data.copy()
data_stat = data.copy()
data_stat2 = data.copy()

st.header("Análisis de Zona")
#Create a dropdown to select the zone
selected_zone = st.selectbox("Seleccionar Zona", data['Zone'].unique(), key='zone_box', index=2) #Add a dropdown element
data = data[data['Zone'] == selected_zone]
tot_median = round(data['Price_USD'].median(),2) #Calculate total price median
m2_median = round(data['Price_m2_USD'].median(),2) #Calculate price per sqmt median
#Print the average price for the selection & the number of observations available
st.write('<html lang="es"><html translate="no">', 'El precio medio por m² en', selected_zone, 'es de ', "$"+str("{:,}".format(m2_median)+"."), 'Este calculo fue realizado en base a', str("{:,}".format(data.shape[0])), 'propiedades. El precio medio total es de', "$"+str("{:,}".format(tot_median)+"."), unsafe_allow_html=True)


st.text("")
st.subheader("Filtra Propiedades dependiendo del # de habitaciones")
#Catch instances in which all properties have the same number of bedrooms
if (data['Bedrooms'].nunique() == 1):
    how_many_bedrooms =  min(data['Bedrooms'])
else:
    #Create a slider to select the number of bedrooms
    how_many_bedrooms = st.slider("Selecciona el # de habitaciones", min(data['Bedrooms']), max(data['Bedrooms']), value=3) #Add a slider element
#Filter by the selected number of bedrooms
data_bedrooms = data[data['Bedrooms'] == how_many_bedrooms]
#Try and except, for the cases in which there aren't any properties with the selected # of bedrooms
try:
    tot_median_bdr = round(data_bedrooms['Price_USD'].median(),2) #Calculate total price median
    m2_median_bdr = round(data_bedrooms['Price_m2_USD'].median(),2) #Calculate price per sqmt median
    #Print the average price for the selection of both zone and # of bedrooms
    st.write('<html lang="es"><html translate="no">', "El precio medio por m² para", selected_zone, ", en propiedades con", str("{:,}".format(how_many_bedrooms)), "habitaciones, es de ", "$"+str("{:,}".format(m2_median_bdr)+"."), "Este calculo fue realizado en base a", str("{:,}".format(data_bedrooms.shape[0])),"propiedades. El precio medio total es de", "$"+str("{:,}".format(tot_median_bdr)+"."), unsafe_allow_html=True)
    #Create a map based on a query to the dataframe
    st.text("")
    st.map(data.query("Bedrooms == @how_many_bedrooms")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider
except:
    how_many_bedrooms_2 = 3
    st.write('<html lang="es"><html translate="no">', "No pudimos encontrar propiedades con",  str("{:,}".format(how_many_bedrooms)), "habitaciones, en", selected_zone, ". Por lo tanto, hemos decidido mostrar los resultados para propiedades de",  str("{:,}".format(how_many_bedrooms_2)), "habitaciones.", unsafe_allow_html=True)
    st.text("")
    data_bedrooms = data[data['Bedrooms'] == how_many_bedrooms_2]
    tot_median_bdr = round(data_bedrooms['Price_USD'].median(),2) #Calculate total price median
    m2_median_bdr = round(data_bedrooms['Price_m2_USD'].median(),2) #Calculate price per sqmt median
    #Print the average price for the selection of both zone and # of bedrooms
    st.write('<html lang="es"><html translate="no">', "El precio medio por m² para", selected_zone, ", en propiedades con", str("{:,}".format(how_many_bedrooms_2)), "habitaciones, es de ", "$"+str("{:,}".format(m2_median_bdr)+"."), "Este calculo fue realizado en base a", str("{:,}".format(data_bedrooms.shape[0])),"propiedades. El precio medio total es de", "$"+str("{:,}".format(tot_median_bdr)+"."), unsafe_allow_html=True)
    st.text("")
    #Create a map based on a query to the dataframe
    st.map(data.query("Bedrooms == @how_many_bedrooms_2")[['latitude', 'longitude']].dropna(how = 'any')) #We use the @ to query the variable created for the slider

#Disclaimer
st.markdown(
    """<small> *Precio medio se refiere a la <a href="https://es.wikipedia.org/wiki/Mediana_(estad%C3%ADstica)#:~:text=En%20el%20%C3%A1mbito%20de%20la,Se%20le%20denota%20mediana." target="_blank"> mediana (estadística)</a>. </small>""", unsafe_allow_html=True,
)
#Disclaimer
st.write('<html lang="es"><html translate="no">', "<small> *No todas las propiedades son desplegadas en el mapa. Debido a la forma en que se recolectan los datos, la latitud y longitud pueden ser un área general, por consiguiente, habrá un traslape en ciertos puntos. No obstante, el número de propiedades analizadas desplegado es preciso. </small>", unsafe_allow_html=True)


st.text("")
st.subheader("Propiedades por Precio por m²")
#Explanation
st.write('<html lang="es"><html translate="no">', "Este mapa representa la distribución de las propiedades disponibles en", selected_zone, ". La altura y el color de las barras representan el precio en US$ por m².", unsafe_allow_html=True)
st.text("")

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
st.write('<html lang="es"><html translate="no">', "<small> *Debido a la forma en la que se recolectan los datos para la latitud y longitud, la delimitación de las zonas en el mapa puede no ser precisa en ciertas ocasiones, no obstante, la clasificación de zona de la propiedad como tal, si es precisa, por consiguiente, los cálculos de precios medios y cualquier otra métrica también serán precisos. </small>", unsafe_allow_html=True)


st.text("")
st.text("")
st.header("Promedios por Zona")
#Explanation
st.write('<html lang="es"><html translate="no">', "El gráfico de barras se encuentra ordenado según el precio promedio por m² de cada zona. El color de cada barra representa el precio promedio total para cada zona, es decir, el promedio de los precios de lista de cada propiedad.", unsafe_allow_html=True)
st.text("")

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
st.write('<html lang="es"><html translate="no">', "Esta sección contiene diferentes análisis estadísticos para la zona seleccionada. La idea es entender mejor la distribución de precios de las propiedades, y a un nivel macro, poder tener una idea de que tan importante es el tamaño de los bienes para predecir su precio total.", unsafe_allow_html=True)
st.text("")

#Create a slider to select the zone
selected_zone_stat = st.selectbox("Seleccionar Zona", data_stat['Zone'].unique(), key='zone_box_stat', index=2) #Add a dropdown element
data_stat = data_stat[data_stat['Zone'] == selected_zone_stat]

st.write('<html lang="es"><html translate="no">', "Distribución de precios para propiedades en", selected_zone_stat, ".", unsafe_allow_html=True)
st.text("")

#Create a radio button to select the type of price to analyze
hist_var = st.radio("¿Deseas analizar precios totales (precio de lista) o precios por m²?",('Precios Totales', 'Precios por m²'), key='histogram_radio')

if hist_var == 'Precios Totales':
    hist_x = "Price_USD"
else:
    hist_x = "Price_m2_USD"

#Create histogram for price by m2 (filtered by zone)
fig_hist = px.histogram(data_stat, x=hist_x, labels=dict(Price_USD="Precio en US$", Price_m2_USD="Precio por m² (US$)"))
fig_hist.layout.yaxis.title.text = 'Número de Propiedades' #Rename y-axis label
st.plotly_chart(fig_hist, use_container_width=True) #write the figure in the web app and make it responsive
#Explanation on distinction between mean and median
st.write('<html lang="es"><html translate="no">', "Nótese que el centro de masa no es el precio medio (mediana) de", "$"+str("{:,}".format(round(data_stat[hist_x].median(),2))), "que se reporta en la sección de Análisis de Zona, sino el precio promedio, el cual es de", "$"+str("{:,}".format(round(data_stat[hist_x].mean(),2))), "para", selected_zone_stat, ".", unsafe_allow_html=True)
st.text("")

st.subheader("Relación entre Precio (US$) y Superficie (m²)")
#Create scatter plot (filtered by zone)
fig_scatter = px.scatter(data_stat, x='Surface', y='Price_USD', trendline="ols", color='Price_m2_USD',
                labels=dict(Surface="Superficie en m²", Price_USD="Precio en US$", Price_m2_USD="Precio por m² (US$)"))
st.plotly_chart(fig_scatter, use_container_width=True) #write the figure in the web app and make it responsive

#Get results from the linear regression
results = px.get_trendline_results(fig_scatter)
results_summary = results.px_fit_results.iloc[0].summary()

#Note that tables is a list. The table at index 1 is the "core" table. Additionally, read_html puts dfs in a list, so we want index 0
#Credit to: https://stackoverflow.com/questions/51734180/converting-statsmodels-summary-object-to-pandas-dataframe/52976810
results_as_html = results_summary.tables[0].as_html()
reg_results = pd.read_html(results_as_html, header=None, index_col=0)[0] #Read as df
r_squared = reg_results.loc['Dep. Variable:'][3] #Extract R-Squared
st.write('<html lang="es"><html translate="no">' ,"En función del modelo desplegado en el gráfico de dispersión, se puede notar que para la", selected_zone_stat, ", el", "{:.0%}".format(r_squared), "de la varianza en el precio puede ser predicha basándose en la cantidad de m² de la propiedad.", unsafe_allow_html=True)
st.text("")
st.write('<html lang="es"><html translate="no">', "Cuanto más alto este porcentaje, mayor es la dependencia del precio en función de la superficie. Esto podría indicar que otras variables son menos significativas. Por otra parte, si el porcentaje es bajo, puede ser que otras variables que no están siendo consideradas en este análisis tengan un mayor efecto en el precio, por ejemplo, la plusvalía de la zona, seguridad, proximidad a puntos de interés, etc.", unsafe_allow_html=True)
st.text("")
st.markdown("""Por último, también se sugiere considerar la cantidad de observaciones que son parte del análisis, ya que el tamaño de la muestra también puede afectar el <a href="https://es.wikipedia.org/wiki/Coeficiente_de_determinaci%C3%B3n" target="_blank"> coeficiente de determinación.</a>""", unsafe_allow_html=True)


st.text("")
#Comparison between Zones
st.subheader("Comparación de distribución de precios entre Zonas")
selected_zone_stat2 = st.selectbox("Seleccionar una segunda Zona para realizar la comparación.", data_stat2['Zone'].unique(), key='zone_box_2',index=3) #Add a dropdown element
data_stat2 = data_stat2[data_stat2['Zone'] == selected_zone_stat2]

#Create a radio button to select the type of price to analyze
comp_hist_var = st.radio("¿Deseas analizar precios totales (precio de lista) o precios por m²?",('Precios Totales', 'Precios por m²'), key='comparison_histogram_radio')

if comp_hist_var == 'Precios Totales':
    comp_hist_x = "Price_USD"
    comp_label = "Precio en US$"
else:
    comp_hist_x = "Price_m2_USD"
    comp_label = "Precio por m² (US$)"

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
st.write('<html lang="es"><html translate="no">', "El precio promedio para", selected_zone_stat, "es de", "$"+str("{:,}".format(round(data_stat[comp_hist_x].mean(),2))), ", mientras que el precio promedio para", selected_zone_stat2, "es de", "$"+str("{:,}".format(round(data_stat2[comp_hist_x].mean(),2)))+".", unsafe_allow_html=True)
st.text("")
st.write('<html lang="es"><html translate="no">', "Se recomienda también tomar en cuenta el precio medio debido a que es menos sensible a valores atípicos. El precio medio para", selected_zone_stat, "es de", "$"+str("{:,}".format(round(data_stat[comp_hist_x].median(),2))), ", y para", selected_zone_stat2, "es de", "$"+str("{:,}".format(round(data_stat2[comp_hist_x].median(),2)))+".", unsafe_allow_html=True)


st.text("")
st.text("")
st.subheader("Datos Crudos")
st.write('<html lang="es"><html translate="no">', 'Al hacer clic en la caja "Mostrar datos", se desplegará la tabla con los datos para la zona seleccionada. Además, es posible descargar la tabla en formato CSV haciendo clic en el enlace que se encuentra debajo de la tabla.', unsafe_allow_html=True)
st.text("")
#Review the raw data (dataframe) in the app
if st.checkbox('Mostrar datos', False): #Creates a checkbox to show/hide the data
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
#st.write('<html lang="es"><html translate="no">', "<small> Construido por Omar Eduardo Martinez. </small>", unsafe_allow_html=True)
st.text("")
st.write('<html lang="es"><html translate="no">', 'Para cualquier sugerencia o reportar errores, por favor contáctame <a href="mailto:omartinez1821992@gmail.com">aquí.</a>', unsafe_allow_html=True)

#Hide hamburger menu & footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 