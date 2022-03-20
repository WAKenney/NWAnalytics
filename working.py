
import base64
from distutils.fancy_getopt import wrap_text
import io
from math import isnan
from os import name
from tkinter import HIDDEN
from tokenize import Name
from attr import field
import folium
# import geemap
import geopandas as gpd
import pandas as pd
# import plotly
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
# from branca.element import MacroElement, Template
from folium.plugins import FloatImage
from folium.plugins import Fullscreen
from PIL import Image
from streamlit.state.session_state import SessionState
from streamlit_folium import folium_static

from geopandas import GeoDataFrame

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode

# st.set_page_config(layout="centered")

currentDir = "https://raw.githubusercontent.com/WAKenney/NWAnalytics/main/"

colTitles=['tree_name', 'species', 'genus', 'family', 'street', 'address', 'location_code', 'ownership_code', 'number_of_stems', 'dbh',
    'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'reduced_crown', 'unbalanced_crown', 'defoliation',
    'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean', 'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks',
    'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space','crack', 'girdling_roots', 'exposed_roots', 'recent_trenching', 'cable_or_brace',
    'wire_conflict', 'sidewalk_conflict', 'structure_conflict', 'tree_conflict', 'sign_conflict', 'comments', 'demerits',
    'simple_rating', 'cpa', 'rdbh', 'rdbh_class', 'dbh_class', 'native', 'suitability', 'defects', 'invasivity', 'seRegion']
    

stringColumns=['tree_name','description', 'species', 'genus', 'family', 'street', 'address','location_code',
    'ownership_code', 'cable_or_brace','wire_conflict', 'sidewalk_conflict','structure_conflict',
    'tree_conflict', 'sign_conflict', 'comments', 'simple_rating', 'rdbh_class',
    'dbh_class', 'native','suitability', 'defects', 'invasivity', 'seRegion']

numericalColumns = ['number_of_stems', 'dbh', 'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'demerits','cpa', 'rdbh']

condColumns = ['reduced_crown', 'unbalanced_crown', 'defoliation', 'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean',
    'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space',
    'crack', 'girdling_roots', 'exposed_roots', 'recent_trenching']

codes={'No major defects':"DarkGreen", 'Major health defect':'ForestGreen', 'Major structural defect(s)':'FireBrick',
    'Major structural AND health defect(s)':'DarkRed', 'N/A':'DimGrey' } #steup colour codes for levels of tree condition

CondcolorOrder = {'defects' : ['No major defects', 'Major health defect', 'Major structural defect(s)',
                            'Major structural AND health defect(s)', 'Condition was not assessed']}# setup order for legend

titleCol1, titleCol2, titleCol3 =st.columns((1,4,1))
title = currentDir + 'NWAnalyticsTitle.jpg'

titleCol2.image(title, use_column_width=True)

mainScreen =st.empty()
filterResultHeader = st.empty()
getFileScreen = st.sidebar.empty()

fileName ='empty'

df = pd.DataFrame()

fileName = getFileScreen.file_uploader("Browse for or drag and drop the name of your Neighburwoods MS excel workbook", 
    type = ['xlsm', 'xlsx'], 
    key ='fileNameKey')

@st.experimental_memo(show_spinner=False)
def getData(fileName):

    '''
    Fetch the data using the fileName chosen above as well as the species table
    
    '''

    if fileName is not None:

        df = pd.read_excel(fileName, sheet_name = "summary", header = 1)
    
    speciesFile = currentDir + 'NWspecies060222.xlsx'
    speciesTable = pd.read_excel(speciesFile,sheet_name = "species")

    # Standardize column names to lower case and hyphenated (no spaces).
    df=df.rename(columns = {'Tree Name':'tree_name','Description':'description','Longitude':'longitude',
                                'Latitude':'latitude','Date':'date','Block ID':'block','Tree Number':'tree_number',
                                'Species':'species','Genus':'genus','Family':'family','Street':'street',
                                'Address':'address','Location Code':'location_code','Ownership Code':'ownership_code',
                                'Crown Width':'crown_width','Number of Stems':'number_of_stems','DBH':'dbh',
                                'Hard Surface':'hard_surface','Ht to Crown Base':'height_to_crown_base',
                                'Total Height':'total_height','Reduced Crown':'reduced_crown','Unbalanced Crown':'unbalanced_crown',
                                'Defoliation':'defoliation','Weak or Yellowing Foliage':'weak_or_yellow_foliage',
                                'Dead or Broken Branch':'dead_or_broken_branch','Lean':'lean','Poor Branch Attachment':'poor_branch_attachment',
                                'Branch Scars':'branch_scars','Trunk Scars':'trunk_scars','Conks':'conks','Rot or Cavity - Branch':'branch_rot_or_cavity',
                                'Rot or Cavity - Trunk':'trunk_rot_or_cavity','Confined Space':'confined_space',
                                'Crack':'crack','Girdling Roots':'girdling_roots', 'Exposed Roots': 'exposed_roots', 'Recent Trenching':'recent_trenching',
                                'Cable or Brace':'cable_or_brace','Conflict with Wires':'wire_conflict',
                                'Conflict with Sidewalk':'sidewalk_conflict','Conflict with Structure':'structure_conflict',
                                'Conflict with Another Tree':'tree_conflict','Conflict with Traffic Sign':'sign_conflict',
                                'Comments':'comments', 'Total Demerits':'demerits','Simple Rating':'simple_rating',
                                'Crown Projection Area (CPA)':'cpa', 'Relative DBH':'rdbh','Relative DBH Class':'rdbh_class',
                                'DBH class':'dbh_class','Native':'native','Species Suitability':'suitability','Structural Defect':'structural', 
                                'Health Defect':'health'})

    def defect_setup(df):
        """
        This def adds a column to the dataframe containing text descriptions for the level of defects based on the yes or no 
        respones in the structural and health columns of the input data.
        """
    
        if ((df['structural'] == 'no') & (df['health'] =='no')):
            return 'No major defects'
        elif ((df['structural'] == 'yes') & (df['health'] =='no')):
            return 'Major structural defect(s)'
        elif ((df['structural'] == 'no') & (df['health'] =='yes')):
            return 'Major health defect(s)'
        elif ((df['structural'] == 'yes') & (df['health'] =='yes')):
            return 'Major structural AND health defect(s)'
        else:
            return 'Condition was not assessed'

    df['defects'] = df.apply(defect_setup, axis = 1)
    
    def setDefectColour(df):
        ''' sets a colour name in column defectColour based on the value in column defects'''
        
        if df['defects'] == 'No major defects':
            return 'darkgreen'

        elif df['defects'] == 'Major structural defect(s)':
            return 'yellow'
        
        elif df['defects'] == 'Major health defect(s)':
            return 'greenyellow'

        elif df['defects'] == 'Major structural AND health defect(s)':
            return 'red'
        
        else:
            return 'gray'

    df['defectColour'] = df.apply(setDefectColour, axis = 1)

    df = pd.merge(df, speciesTable[['species', 'diversity_level', 'invasivity']], on="species", how="left", sort=False)
    
    df = pd.merge(df, speciesTable[['species', 'seRegion']], on="species", how="left", sort=False)

    df = pd.merge(df, speciesTable[['species', 'color']], on="species", how="left", sort=False)

    df.loc[(df.invasivity =='invasive'), 'suitability'] = 'Very Poor'

    df.merge(speciesTable, how = 'left', on = 'species', sort = False )

    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude)).copy() # save the 'data' pandas dataframe to a geodataframe

    df = df.set_crs('epsg:4326') # set coordinate reference system to WGS84
    
    df['date'] = df['date'].astype(str) # Save the inventory dates as a string.  Otherwise an error is thrown when mapping

    colorsTable = pd.read_excel(speciesFile,sheet_name = "colors")
    
    colorsTable.set_index('taxon', inplace = True)

    return [df, speciesTable, colorsTable]


def agFilter(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_default_column(editable=True, filter=True)

    gb.configure_column(field='tree_name', header_name='Tree Name')
    gb.configure_column(field='description', header_name='Tree Description',
        editable=False, filter = False, wrapText=True, autoHeight = True)
    gb.configure_column(field='latitude', hide = True)
    gb.configure_column(field='longitude', hide = True)
    gb.configure_column(field='date', editable=True)
    gb.configure_column(field='block', header_name ='Block Code', editable=True)
    gb.configure_column(field='tree_number', header_name ='Tree Number', editable=True)
    gb.configure_column(field='species', header_name = 'Species', editable=True)
    gb.configure_column(field='genus', header_name = 'Genus', editable=True)
    gb.configure_column(field='family', header_name = 'Family', editable=True)
    gb.configure_column(field='street', header_name='Street', editable=True)

    gb.configure_column(field='reduced_crown', header_name='Reduced Crown', editable=True)
    gb.configure_column(field='unbalanced_crown', header_name='Unbalanced Crown', editable=True)
    gb.configure_column(field='defoliation', header_name='Defoliation', editable=True)
    gb.configure_column(field='weak_or_yellow_foliage', header_name='Weak or Yellow Foliage', editable=True)
    gb.configure_column(field='dead_or_broken_branch', header_name='Dead or Broken Branch', editable=True)
    gb.configure_column(field='lean', header_name='Lean', editable=True)
    gb.configure_column(field='poor_branch_attachment', header_name='Poor Branch Attachment', editable=True)
    gb.configure_column(field='branch_scars', header_name='Branch Scars', editable=True)
    gb.configure_column(field='trunk_scars', header_name='Trunk Scars', editable=True)
    gb.configure_column(field='conks', header_name='Conks', editable=True)
    gb.configure_column(field='branch_rot_or_cavity', header_name='Branch Rot or Cavity', editable=True)
    gb.configure_column(field='trunk_rot_or_cavity', header_name='Trunk Rot or Cavity', editable=True)
    gb.configure_column(field='confined_space', header_name='Confined Space', editable=True)

    gb.configure_column(field='geometry', hide = True)
    gb.configure_column(field='defectColour', hide = True)
    gb.configure_column(field='diversity_level', hide = True)
    gb.configure_column(field='demerits', hide = True)
    gb.configure_column(field='seRegion', header_name='Origin')
    gb.configure_column(field='structural', header_name='Structural Defect(s)')
    gb.configure_column(field='health', header_name='Health Defect(s)')
    gb.configure_column(field='defects', header_name='Defect Summary')

    gridOptions = gb.build()

    gridReturn = AgGrid(df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        height = 500, 
        theme = 'blue',
        enable_enterprise_modules=True, # enables right click and fancy features - can add license key as another parameter (license_key='string') if you have one
        key='select_grid', # stops grid from re-initialising every time the script is run
        reload_data=True, # allows modifications to loaded_data to update this same grid entity
        # update_mode=GridUpdateMode.FILTERING_CHANGED,
        update_mode=GridUpdateMode.MANUAL,
        data_return_mode="FILTERED_AND_SORTED")


    towrite = io.BytesIO()
    downloaded_file = gridReturn['data'].to_excel(towrite, encoding='utf-8', index=False, header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()  # some strings
    linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="NwAnalyticsData.xlsx">Click here to save your data as an Excel file</a>'
    st.markdown(linko, unsafe_allow_html=True)

    return gridReturn['data']
    

def mapItFolium(mapData):

    if mapData.empty:
        st.warning("Be sure to finish selecting the filtering values in the sidebar to the left.")

    # mapData = mapData[mapData['latitude'].notna()].copy()
    mapData = mapData[mapData['latitude'].notna()] # Drop entries with no latitude or longitude values entered
    mapData = mapData[mapData['longitude'].notna()]

    mapData['crown_radius'] = mapData['crown_width']/2

    avLat = mapData['latitude'].mean()  #calculate the average Latitude value and average Longitude value to use to centre the map
    avLon = mapData['longitude'].mean()
    
    avLat=mapData['latitude'].mean()
    avLon=mapData['longitude'].mean()
    maxLat=mapData['latitude'].max()
    minLat=mapData['latitude'].min()
    maxLon=mapData['longitude'].max()
    minLon=mapData['longitude'].min()
    
    treeMap = folium.Map(location=[avLat, avLon],  
        zoom_start=5,
        max_zoom=75, 
        min_zoom=1, 
        width ='100%', height = '100%', 
        prefer_canvas=True, 
        control_scale=True,
        tiles='OpenStreetMap'
        )

    treeMap.fit_bounds([[minLat,minLon], [maxLat,maxLon]])

    mapData.apply(lambda mapData:folium.CircleMarker(location=[mapData["latitude"], mapData["longitude"]], 
        # color=mapData['defectColour'],
        # color='#000000',
        color='white', 
        stroke = True,
        weight = 2,
        fill = True,
        fill_color=mapData['defectColour'],
        fill_opacity = 0.6,
        line_color='#000000',
        radius= 5,
        tooltip = mapData['tree_name'],
        popup = folium.Popup(mapData["description"], 
        name = "Points",
        max_width=450, 
        min_width=300)).add_to(treeMap), 
        axis=1)

    folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Satellite',
        overlay = False,
        control = True
       ).add_to(treeMap)

    Fullscreen().add_to(treeMap)

    folium.LayerControl().add_to(treeMap)
   
    folium_static(treeMap)

df = getData(fileName)

if fileName is not None:
    # getFileScreen = st.empty()
    with st.spinner(text = 'Setting up your data, please wait...'):
        df = getData(fileName)[0]
        speciesTable = getData(fileName)[1]
        colorsTable = getData(fileName)[2]
        colorsDict = colorsTable.to_dict('dict')['color']


select_df = agFilter(df)

mapItFolium(select_df)
