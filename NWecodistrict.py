import pandas as pd
import geopandas as gpd
import streamlit as st
from shapely.geometry import Point

import folium
from streamlit_folium import folium_static

# def get_ecodistrict(data)
#calculate the average Latitude value and average Longitude value to use to centre the map
    # avLat = data['latitude'].mean()  
    # avLon = data['longitude'].mean()

currentDir = "https://raw.githubusercontent.com/WAKenney/NWAnalytics/main/"

avlat = 45.409106576109394
avlon = -75.70343486759252

@st.cache_data(show_spinner=True)
def get_ecodistricts():

    ''' import the geopackage with the Ecodistricts'''
    
    ecod = gpd.read_file(currentDir + "OntarioEcodistricts.gpkg")
    ecod.drop(['GEOMETRY_U', 'EFFECTIVE_', 'SYSTEM_DAT', 'OGF_ID', 
                'SHAPE.AREA', 'SHAPE.LEN', 'OBJECTID'], axis=1, inplace=True)

    ecod.rename(columns={'ECODISTR_1': 'ecodistrict', 
        'ECODISTRIC':'ecodistrict_name', 'ECOREGION_':'ecoregion_name',
        'ECOREGIO_1':'ecoregion', 'ECOZONE_NA':'ecozone_name'}, inplace = True)
        
    ecod = ecod.to_crs('EPSG:4326')

    return ecod

ecod = get_ecodistricts()

pointDf = pd.DataFrame(
    {'Name': '"Averge" Point',
    'latitude': avlat,
    'longitude': avlon
    }, index=[0])

pointgdf = gpd.GeoDataFrame(
    pointDf, geometry=gpd.points_from_xy(pointDf.longitude, pointDf.latitude))

pip = gpd.tools.sjoin(pointgdf, ecod, predicate="within", how='left')

ecodName = (pip.ecodistrict[0])

st.write("Ecodistrict: ", ecodName)


########## Map the ecodistricts and show the point of avlat and avlon #################

def mapEcod():

    st.spinner("Please wait while your map is set up.")

    ecodMap = ecod.explore()

    folium.CircleMarker(location=[avlat, avlon],
                zoom_start = 9, 
                color='white', # use a white border on the circle marker so it will show up on satellite image
                stroke = True,
                weight = 2,
                fill = True,
                fill_color='red',
                fill_opacity = 0.2,
                line_color='#000000',
                tooltip = ecod['ecodistrict'],
                ).add_to(ecodMap)

    folium_static(ecodMap)

mapButton = st.button('Click here to map the point and ecodistrict')

if mapButton:

    mapEcod()

