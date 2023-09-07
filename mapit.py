import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode

@st.experimental_memo(show_spinner=False)
def get_data():

    ''' import the geopackage with the Ecodistriicts'''
    
    polyGdf = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioEcodistricts.gpkg")
    polyGdf.drop(['GEOMETRY_U', 'EFFECTIVE_', 'SYSTEM_DAT', 'OGF_ID',
        'SHAPE.AREA', 'SHAPE.LEN', 'OBJECTID'], axis=1, inplace=True)

    polyGdf.rename(columns={'ECODISTR_1': 'ecodistrict', 
        'ECODISTRIC':'ecodistrict_name', 'ECOREGION_':'ecoregion_name',
        'ECOREGIO_1':'ecoregion', 'ECOZONE_NA':'ecozone_name'}, inplace = True)
        
    polyGdf = polyGdf.to_crs('EPSG:4326')

    return polyGdf

polyGdf = get_data()

pointDf = pd.DataFrame(
    {'Name': ['Home', 'Cottage'],
    'latitude': [44.988780766840776, 44.788710],
    'longitude': [-76.39646887779236, -76.327595]
    })

pointGdf = gpd.GeoDataFrame(pointDf, geometry=gpd.points_from_xy(pointDf.longitude, pointDf.latitude), crs = 'EPSG:4326')


st.write(pointGdf)

myMap = polyGdf.explore()

pointGdf.apply(lambda mapData:folium.CircleMarker(location=[mapData["latitude"],
            mapData["longitude"]],
            color='white', # use a white border on the circle marker so it will show up on satellite image
            stroke = True,
            weight = 2,
            fill = True,
            fill_color='red',
            fill_opacity = 0.2,
            line_color='#000000',
            # radius= pointSizeSlider, #setup a slide so the use can chage the size of the marker
            tooltip = mapData['Name'],
            ).add_to(myMap), 
            axis=1)

folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Satellite',
        overlay = False,
        control = True
    ).add_to(myMap)


#     # add a fullscreen option and layer control to the map
Fullscreen().add_to(myMap)
folium.LayerControl().add_to(myMap)

folium_static(myMap)

# folium.GeoJson(data = LCgdf, name = 'Least Cost Path (yellow)', style_function=lambda x: {'fillColor': 'yellow'}).add_to(fcfMap)
