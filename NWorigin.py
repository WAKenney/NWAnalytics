
import geopandas as gpd
import webbrowser
import pandas as pd
import fiona
import folium
# import ee  # Needed for satelite map
# import geehydro  # Needed for satelite map
# import plotly
import plotly.graph_objects as go
import streamlit as st


st.header("Species Origin (Native vs Introduced)")

ecod = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioEcodistricts.gpkg")
ecod = ecod.to_crs(3857)

# speciesFile = r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\NWspecies080122.xlsx"
speciesFile = r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\NWOrigin.csv"

speciesTable = pd.read_csv(speciesFile)

speciesMaps = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioLittleMaps epsg4269.gpkg")

nwCodeList = speciesTable.species_code.tolist()
mapList = fiona.listlayers(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioLittleMaps epsg4269.gpkg")


def sppOrigin(spp, ecodistrict):
    #   The following works except if no map is available
    
    sciCode = speciesTable.loc[speciesTable['species_code'] == spp, 'scientific_code'].iloc[0]

    if sciCode not in mapList:
        filt = (speciesTable['species_code'] == spp)
        speciesTable.loc[filt, ecodistrict] = "introduced"

    else:

        latinCode = speciesTable.loc[speciesTable['species_code'] == spp, 'scientific_code'].iloc[0]

        species = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioLittleMaps epsg4269.gpkg",layer = latinCode).dissolve()

        species = species .to_crs(3857)

        filtEco = (ecod['ECODISTR_1']==ecodistrict)
        
        eco = ecod.loc[filtEco]  

        ecoArea = eco.area.iloc[0]

        over = species.overlay(eco, how='intersection', keep_geom_type=None, make_valid=True)

        zeroTest = len(over.AREA.value_counts()) > 0

        if zeroTest == True:
            
            overArea = over.area.iloc[0]

            coverage = int(((overArea/ecoArea)*100).round(0))

            if coverage<5:
                
                filt = (speciesTable['species_code'] == spp)
                speciesTable.loc[filt, ecodistrict] = "introduced"

            else:
                filt = (speciesTable['species_code'] == spp)

                speciesTable.loc[filt, ecodistrict] = "native"

        else:
            filt = (speciesTable['species_code'] == spp)
            speciesTable.loc[filt, ecodistrict] = "introduced"

    return speciesTable


def showTable():
    cols = ['species_code','scientific_code','scientific_name']
        
    tab = go.Figure(go.Table(
        
        columnwidth = [20,80],
        
        header=dict(values=list(cols),
                    fill_color='lightgreen',
                    align='center'),
        cells=dict(values=[df[col] for col in cols],
                    fill_color='lavender',
                    # line_color ='black',
                    align='center')))
            
    tableWidth = st.slider('Set table width',min_value=500, max_value=1400, step = 100, value = 500)
    tab.layout.width=tableWidth
    tab.layout.height=800
    tab.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(tab)


def mapIt():
    ecoDistFMap = folium.Map(location=[45.424289, -75.536940],  
        fill_color="green",
        zoom_start = 10,
        max_zoom=15, 
        min_zoom=1, 
        width ='100%', height = '100%', 
        prefer_canvas=True, 
        control_scale=True,
        tiles='OpenStreetMap',
        attr='Mapbox Attribution'
        )

    ecoDistGeojson = folium.GeoJson(ecod, 
            name="Ecodistricts").add_to(ecoDistFMap)

    folium.GeoJsonTooltip(fields=['ECODISTR_1']).add_to(ecoDistGeojson)

    ecoDistFMap.setOptions('HYBRID')
    ecoDistFMap.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)

    ecoDistFMap.save(r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\ecoDistMap.html")
    webbrowser.open(r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\ecoDistMap.html")

    

def mapAvailability():
    speciesMaps = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioLittleMaps epsg4269.gpkg")
    nwCodeList = speciesTable.species_code.tolist()
    latinCodeList = speciesTable.scientific_code.tolist()
    mapList = fiona.listlayers(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioLittleMaps epsg4269.gpkg")
    
    mapList = mapList.astype(str)

    for lcode in latinCodeList:
        filt = speciesTable.loc[speciesTable['scientific_code'] == lcode, 'diversity_level'].iloc[0]
        if filt == 'species':
            if lcode in mapList:
                speciesTable.loc[speciesTable['scientific_code'] == lcode, 'Map'] = 'Map'
            else:
                speciesTable.loc[speciesTable['scientific_code'] == lcode, 'Map'] = 'NO Map'
    else:
        speciesTable.loc[speciesTable['scientific_code'] == lcode, 'Map'] = 'n/a'

    speciesTable.to_csv(r"C:\Users\HP\Documents\Data\Files\Neighbourwoods\Master files\NWAalytics3\mapAvailability.csv")        


if st.button('Generate origin table for all species and ecodistricts'):

    for edist in ['6E-1', '6E-2','6E-4', '6E-5', '6E-6']:

    # edist = '6E-1',

        for spp in nwCodeList:

            df = sppOrigin(spp=spp, ecodistrict = edist)
            # filt = (speciesTable['species_code'] == spp)
            # n = speciesTable.loc[filt, 'native']
            # st.write(spp)

    df.to_csv(r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\LetsTryAgain.csv")

if st.button("Show table?"):
    showTable()

if st.button("show the map?"):   
    mapIt()

if st.button('Check map availability'):
    mapAvailability()