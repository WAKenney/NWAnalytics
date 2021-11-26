# -*- coding: utf-8 -*-
"""
Created on November 26 2021

@author: W.A. Kenney
"""

# import time
import base64
import io
from logging import _STYLES
from math import isnan
from types import GetSetDescriptorType

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from branca.element import MacroElement, Template
from folium.plugins import FloatImage
# import dash
# import dash_table
from PIL import Image
# import os
from streamlit.state.session_state import SessionState
from streamlit_folium import folium_static
from typing_extensions import ParamSpec

st.set_page_config(layout="wide")

# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

# currentDir = "https://raw.githubusercontent.com/WAKenney/Neighbourwoods/main/"
# currentDir ='https://github.com/WAKenney/NWAnalytics'
# currentDir = "C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\"

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
# title = currentDir + 'NWAnalyticsTitle.jpg'
title = 'NWAnalyticsTitle.jpg'
titleCol2.image(title, use_column_width=True)

with st.expander("Click here for help in getting started.", expanded=False):
        st.markdown("""
            Neighbour_woods_ is a community-based program to assist community groups in the stewardship of the urban forest in their neighbourhood.
            Using NWAnalytics, you can map and analyze various aspects of the urban forest that will help you develop and implement stewardship strategies.
            At present, you must first have your Neighbourwoods tree inventory data in a Neighbour_woods_ MS excel workbook (version 2.6 or greater).

            To get started, select your Neighbour_woods_ MS excel workbook at the sidebar on the left. Once your data has been uploaded (this may take 
            a few minutes if you have a big file, be patient) you will be asked to select the functions you want to display.  Select as many as you 
            want from the dropdown list AND CLICK ON SUBMIT.  The selected analyses will be shown in the main frame.

            You can conduct these analyses on all of the data, or you can filter the data for specific queries. The "Filter by List" option allows you
            to select a parameter (e.g. species) and then within that parameter build a list of values (e.g. Norway Maple, White Spruce, White Birch). 
            The selected functions or analyses will be carried out for those values in the list.  A more restrictive filter can be carried out with one parameter, 
            for example you could select dbh as the parameter, then select a comparison method of > (greater than) and then a value of 50 cm. The selected functions would be carried out on all trees with dbh values of more than 50 cm.

            But what if you wanted all the Silver Maples with a dbh > 50 cm?  This can be done using the Two Parameter Filter.  Select dbh > 50cm as before 
            but now select AND from the logical operator dropdown list and then select the parameter, comparison methods and value as done before. In this case all of the selected functions will be performed on all the silver maple with a dbh greater than 50 cm.

            You can select a value from the drop down box by scrolling up or down but you can also type the first few letters of the value you want and this should 
            bring you close to thee value in the list where you can click on it to select.

            In various places you will have opportunities to click on a box for more information, just as you are reading this text.  To close these boxes, 
            simply click on the header button again.

            Click on the following link to read more about Neighbourwoods: http://neighbourwoods.org/')

            For support, contact Andy Kenney at:     a.kenney@utoronto.ca
""")

mainScreen =st.empty()
filterResultHeader = st.empty()
getFileScreen = st.sidebar.empty()

fileName = "empty"

df = pd.DataFrame()

fileName = getFileScreen.file_uploader("Browse for or drag and drop the name of your Neighburwoods MS excel workbook", 
    type = "xlsm", 
    key ='fileNameKey')

st.markdown('___')

@st.experimental_memo(show_spinner=False)
def getData(fileName):

    with st.spinner(text = 'Loading your Neighburwoods data, please wait...'):

        if fileName is not None:
            df = pd.read_excel(fileName, sheet_name = "summary", header = 1)

    # speciesFile = currentDir + 'NWspecies041121.csv'
    speciesFile = 'NWspecies041121.csv'
    speciesTable = pd.read_csv(speciesFile)

    # codesFile = currentDir + 'NWcodes180321.csv'
    # codesFile = 'NWcodes180321.csv'
    # codesTable = pd.read_csv(codesFile,encoding='cp1252')

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

    df.loc[(df.invasivity =='invasive'), 'suitability'] = 'Very Poor'

    df.merge(speciesTable, how = 'left', on = 'species', sort = False )

    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude)).copy()

    df = df.set_crs('epsg:4326') # set coordinate reference system to WGS84
    # df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')  #Save the inventory dates as a string.  Otherwise and error is thrown when mapping
    df['date'] = df['date'].astype(str)

    return df

if fileName is not None:
    getFileScreen = st.empty()
    df = getData(fileName)

def setupSidebar(df):
    """
    This def sets up the Sttreamlit sidebar
    """ 
    
    selectFunctionForm = st.sidebar.form(key = 'selectFunction')
    selectFunctionForm.header('Select the function(s) you want to display ')
    selectFunction = selectFunctionForm.multiselect('',['Show Data', 'Map Trees', 'Tree Diversity', 'Species Origin', 'Tree Condition', 'Ralative DBH', 'Species Suitability'])
    selectFunctionForm.form_submit_button("Submit")

    st.sidebar.header("Do you want to FILTER the tree data?")
    filterMenu1 = st.sidebar.empty()
    with filterMenu1:
        
        filtYesOrNo = st.radio("", options =('No, use all the data', 'Yes, filter the data'))

    if filtYesOrNo == 'Yes, filter the data':
        
        filterMenu2 = st.sidebar.empty()
        
        with filterMenu2:         
            filterType = st.radio("Select the type of filter you want to use", options =('Filter by List?', 'One Parameter Filter?', 'Two Parameter Filter?'))
            
        if filterType == 'Filter by List?':
            select_df = simpleFilter(df)
            
        elif filterType == 'One Parameter Filter?':
            select_df = oneParameterFilter(df, 0)
        
        else:
            select_df = twoParameterFilter(df)
                    
    else:  #Don't filter
        select_df = df

    if 'Show Data' in selectFunction:
        showTable(select_df)
        
    if 'Map Trees' in selectFunction:
        mapIt(select_df)
        # mapItFolium(select_df)

    if 'Tree Diversity' in selectFunction:
        diversity(select_df)    

    if 'Species Origin' in selectFunction:
        speciesOrigin(select_df)

    if 'Tree Condition' in selectFunction:
        treeCondition(select_df)
        
    if 'Ralative DBH' in selectFunction:
        relativeDBH(select_df)

    if 'Species Suitability' in selectFunction:
        speciesSuitablity(select_df)

def simpleFilter(data):
    
    filterMenu3 =st.sidebar.empty()
    with filterMenu3:
        select_param = st.sidebar.selectbox('Select a parameter for filtering', colTitles, index = 1)
        value_list = data[select_param]
        value_list =pd.unique(value_list)    

        select_value = st.sidebar.multiselect('Now, select a value for filtering within ' + select_param, value_list)
    
    select_df = data[data[select_param].isin(select_value)].copy()
    
    filterMenu4 =st.sidebar.empty()
    with filterMenu4:
        st.sidebar.subheader("Number of matches = " + str(select_df.shape[0]))
        
    with filterResultHeader:
        st.subheader('The following is based on the data filtered by ' + select_param + ' in the list ' + str(select_value))

    return select_df

###########################

def oneParameterFilter(data, keyCount):
    
    filterMenu3 =st.sidebar.empty()
    with filterMenu3:
        oneSelectParam = st.sidebar.selectbox('Select a parameter for filtering', options = colTitles, index = 2, key = 'oneSelectParam' + str(keyCount))            
    
    if oneSelectParam in stringColumns:
        oneCompMethodOption = ['==', '!=']
        filterMenu4 =st.sidebar.empty()
        with filterMenu4:
            oneCompMethod = st.sidebar.selectbox('Select a method of camparison', options = oneCompMethodOption, key = 'oneCompMethod' + str(keyCount))
    
    elif oneSelectParam in numericalColumns:
        oneCompMethodOption = ['==', '!=', '<', '<=', '>', '>=']
        filterMenu4 =st.sidebar.empty()
        with filterMenu4:
            oneCompMethod = st.sidebar.selectbox('Select a method of camparison', options = oneCompMethodOption, key = 'oneCompMethod' + str(keyCount))
    
    else:
        oneCompMethodOption = ['==', '!=', '<', '<=', '>', '>=']
        filterMenu4 =st.sidebar.empty()
        with filterMenu4:
            oneCompMethod = st.sidebar.selectbox('Select a method of camparison', options = oneCompMethodOption, key = 'oneCompMethod' + str(keyCount))
        
    value_list = data[oneSelectParam]
    value_list =pd.unique(value_list)
    value_list.sort()
    
    filterMenu5 =st.sidebar.empty()
    with filterMenu5:
        
        if oneCompMethod in ['==', '!=']:
            select_value = st.sidebar.selectbox('Now, select a value for filtering within ' + oneSelectParam, value_list, index = 0, key = 'select_value' + str(keyCount))
        else:
            minValue = int(data[oneSelectParam].min())
            maxValue = int(data[oneSelectParam].max())
            
            if oneSelectParam in condColumns:
                select_value = st.sidebar.slider('Now, select a value for filtering within ' + oneSelectParam, minValue, maxValue, step = 1, key = 'select_value' + str(keyCount))
            else:
                select_value = st.sidebar.slider('Now, select a value for filtering within ' + oneSelectParam, minValue, maxValue, key = 'select_value' + str(keyCount))
        
    if oneCompMethod == '==':
        select_df = data.loc[(data[oneSelectParam] ==  select_value)]
    elif oneCompMethod == '!=':
        select_df = data.loc[(data[oneSelectParam] !=  select_value)]
    elif oneCompMethod == '<':
        select_df = data.loc[(data[oneSelectParam] <  select_value)]
    elif oneCompMethod == '<=':
        select_df = data.loc[(data[oneSelectParam] <=  select_value)]
    elif oneCompMethod == '>':
        select_df = data.loc[(data[oneSelectParam] >  select_value)]
    else:
        select_df = df.loc[(data[oneSelectParam] >=  select_value)]
    
    oneQstring =  oneSelectParam + oneCompMethod + str(select_value)

    with filterResultHeader:
        st.subheader('The results are based on the following search string: ' + oneQstring + ' with ' + str(select_df.shape[0]) + ' matches.'  )

    return select_df
        
#############################################################################
def twoParameterFilter(data):
    
    tempdf1 = oneParameterFilter(data, 0)
    
    filterMenu3 = st.sidebar.empty()
    with filterMenu3:
        logOperator = st.sidebar.selectbox('Now select a logical operator', options = ['AND', 'OR']) 
    
    if logOperator == 'AND':
        
        select_df = oneParameterFilter(tempdf1, 1)
      
    else:
        tempdf2 = oneParameterFilter(data, 1)
    
        select_df = tempdf1.append(tempdf2, ignore_index = True)
    
    filterMenu4 = st.sidebar.empty()
    with filterMenu4:
        st.sidebar.subheader("The combined number of matches = " + str(select_df.shape[0]))
    
    with filterResultHeader: #This clears anything that is already in the filterResultsHeader
        st.write("")    

    return select_df
    
##################################################### Show data table ##########################################
def showTable(data):
    """
    This function displays the data, either filtered or not filtered, as a Plotly table.  The user can add columns to the default
    Description and Tree Name columns, and chnge the width of the columns using a Streamlit slider.  The user can also send the data, 
    as it is filtered (or not) to an Excel worksheet.  The exported worksheet will have ALL the columns regardless of which columns were added
    to the Plotly table.  The original data included a defectsClour column, native column and the geometery column.  These are dropped
    from the Data dataframe before sending to the xlsx file.
    """
        
    data_columns = data.columns.values.tolist()

    data.drop(['defectColour', 'native', 'geometry'], axis =1, inplace = True)

    tableCol1, tableCol2 =st.columns(2)

    with tableCol1:   
        selectedCols = st.multiselect('Select the ADDITIONAL columns to show in the table', data_columns)

    cols = ['tree_name','description'] + selectedCols
    
    fig = go.Figure(go.Table(
        
        columnwidth = [20,80],
        
        header=dict(values=list(cols),
                    fill_color='lightgreen',
                    align='center'),
        cells=dict(values=[data[col] for col in cols],
                    fill_color='lavender',
                    # line_color ='black',
                    align='center')))
         
    tableWidth = st.slider('Set table width',min_value=500, max_value=1400, step = 100, value = 500)
    fig.layout.width=tableWidth
    fig.layout.height=800
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(fig)

    with tableCol2:

        towrite = io.BytesIO()
        downloaded_file = data.to_excel(towrite, encoding='utf-8', index=False, header=True)
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode()  # some strings
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx">Download your data as an Excel file</a>'
        st.markdown(linko, unsafe_allow_html=True)
            
    st.markdown('___')
    
##################################################################################################################################
def mapItFolium(mapData):

    '''Map the trees as points using folium.  MapData is the dataframee resulting from the filtering done on the original dataframe
    points are coloured according to theirdefect description
    '''
    mapCol1, mapCol2, mapCol3 = st.columns(3)
    pointSizeSlider = mapCol2.slider('Move the slider to adjust the point size', min_value = 2, max_value = 20, value =10)
        
    
    if mapData.empty:
        st.warning("Be sure to finish selecting the filtering values in the sidebar to the left.")

    mapData = mapData[mapData['latitude'].notna()].copy()

    avLat = mapData['latitude'].mean()  #calculate the average Latitude value and average Longitude value to use to centre the map
    avLon = mapData['longitude'].mean()
    
    avLat=mapData['latitude'].mean()
    avLon=mapData['longitude'].mean()
    maxLat=mapData['latitude'].max()
    minLat=mapData['latitude'].min()
    maxLon=mapData['longitude'].max()
    minLon=mapData['longitude'].min()

    treeMap = folium.Map(location=[avLat, avLon],  
        zoom_start=18,
        max_zoom=28, 
        min_zoom=1, 
        width ='100%', height = '100%', 
        prefer_canvas=True, 
        control_scale=True,
        tiles='OpenStreetMap',
        attr='Mapbox Attribution')

    treeMap.fit_bounds([[minLat,minLon], [maxLat,maxLon]])

    # mapData.apply(lambda mapData:folium.Circle(location=[mapData["latitude"], mapData["longitude"]], 
    #     color=mapData['defectColour'], 
    #     radius= (mapData['crown_width']/2), 
    #     popup = folium.Popup(mapData["description"], 
    #     max_width=450, 
    #     min_width=300)).add_to(treeMap), 
    #     axis=1)

    mapData.apply(lambda mapData:folium.CircleMarker(location=[mapData["latitude"], mapData["longitude"]], 
        color=mapData['defectColour'], 
        radius= pointSizeSlider,
        popup = folium.Popup(mapData["description"], 
        max_width=450, 
        min_width=300)).add_to(treeMap), 
        axis=1)


    mapCol1, mapCol2 = st.columns(2)

    with mapCol1:
        folium_static(treeMap)
    
    
#####################################################
def mapIt(mapData):
    
    if mapData.empty:
        st.warning("Be sure to finish selecting the filtering values in the sidebar to the left.")
        
    avLat = mapData['latitude'].mean()  #calculate the average Latitude value and average Longitude value to use to centre the map
    avLon = mapData['longitude'].mean()
    
    mapData['condColor'] = mapData['defects'].map(codes) # create a column called conColor and map the color values based on 
                                                                #the condition code in the dictionary called condColor
    
    map_df = mapData[mapData['latitude'].notna()]

    mapData['description'] = mapData['description'].str.wrap(10) 
    
    fig = px.scatter_mapbox(data_frame = map_df, lat="latitude", lon="longitude", 
                            hover_name='tree_name',
                            hover_data={"tree_name": False,
                                        "description": False,
                                        'address': True,
                                        'location_code': False,
                                        'ownership_code': False,
                                        'species': True,
                                        'dbh' : True,
                                        'defects': True,
                                        'latitude': False,
                                        'longitude': False     
                                        }, 
                            color=map_df.defects,
                            color_discrete_map  = codes,
                            category_orders = CondcolorOrder,
                            center=dict(lat=avLat, lon=avLon), 
                            zoom=16, height=300,
                            text =map_df['tree_name'],
                            title = 'My Map')
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(autosize=False, width=1200, height=600)
    
    mapCol1, mapCol2, mapCol3 = st.columns(3)
    
    with mapCol1:

        base_map_type = st.radio('Select the type of basemap', options= ['Map', 'Satellite Image'])
        
        if base_map_type == 'Map':       
            fig.update_layout(mapbox_style = 'open-street-map')
        else:
            # useSatellite(fig)
            st.write('To use Google satelite images you will need a free Google Maps API Key.  Go to https://elfsight.com/blog/2018/06/how-to-get-google-maps-api-key-guide/ ')
            mapToken = st.text_input('Enter your Google Maps API Key')
            try:
                fig.update_layout(mapbox_style = 'satellite', mapbox_accesstoken = mapToken )
            except:
                st.warning('Enter your Google Maps token in the box  and press return.')
            
    fig.layout.width=1500
    fig.layout.height=1500
    
    fig.update_layout(legend=dict(yanchor="top",
                                  y=0.99,
                                  xanchor="left",
                                  x=0.01
                                  ))
    
    with mapCol2:
        pointSizeSlider = st.slider('Move the slider to adjust the point size', min_value = 2, max_value = 20, value =10)
        fig.update_traces(marker_size = pointSizeSlider)

    with mapCol3:

        st.subheader("An option to save the map to your hard drive as a static HTML is coming soon..... ")

        # def download_link(object_to_download, download_filename, download_link_text):
        #     """
        #     Generates a link to download the given object_to_download.

        #     object_to_download (str, pd.DataFrame):  The object to be downloaded.
        #     download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
        #     download_link_text (str): Text to display for download link.

        #     Examples:
        #     download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
        #     download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

        #     """
        #     if isinstance(object_to_download,pd.DataFrame):
        #         object_to_download = object_to_download.to_csv(index=False)

        #     # some strings <-> bytes conversions necessary here
        #     b64 = base64.b64encode(object_to_download.encode()).decode()

        #     return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

        # download_link()



        # towrite = io.BytesIO()
        # downloaded_file = data.to_excel(towrite, encoding='utf-8', index=False, header=True)
        # towrite.seek(0)  # reset pointer
        # b64 = base64.b64encode(towrite.read()).decode()  # some strings
        # linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx">Download your data as an Excel file</a>'
        # st.markdown(linko, unsafe_allow_html=True)

    #     size_slider = st.slider('Select the size of the marker on the map', min_value = 5, max_value = 20, value = 10)
    #     fig.update_traces(marker_size = size_slider)

    # with mapCol3:

    #     with st.form(key = 'saveMapFormKey', clear_on_submit=True):
    #         mapName = st.text_input("To save the map, enter a file name and press submit. The map will be saved as an HTML.")
    #         saveMapSubmit = st.form_submit_button('Submit')
            
    #         if saveMapSubmit:

    #             if mapName == '':
    #                 mapName = "map.html"
    #             elif len(mapName) < 5:
    #                 mapName = mapName + '.html'
    #             elif mapName[-5] != '.html':
    #                 mapName = mapName + '.html'

    #             saveMapPath = os.path.join(st.session_state.pathNameKey, mapName)
    #             saveMapPath = saveMapPath.replace('"', '')
    #             st.write(saveMapPath)

    #             plotly.offline.plot(fig, filename = saveMapPath)
    
    st.markdown('___')
    
    st.plotly_chart(fig)
    
    return fig

# ########################################## Diversity ############################################
    
def diversity(data):

    data = data.loc[data['diversity_level'] != 'other']
   
    divLevel = st.radio('Select a level of diversity', ('species', 'genus', 'family'))
    
    st.header('Tree Diversity Summary by ' + divLevel)

    with st.expander("Click here to read some comments and suggestions about diversity.", expanded=False):
        st.markdown("""
            
            The first pie chart illustrates the distribution of the species, genus or family (you can select the level of diversity by selecting the 
            apporpriate radio button at the top) by the frequency or simple count of the number of trees.  But this doesn't tell the whole story. 
            A species (genus or family) could be represented by a large number of small individual trees and the first graph of simple frequency 
            would indicate that species' significance.  However, another species (genus or family) could have fewer individuals (lower frequency) 
            but of much larger size and hence a great impact on urban forest benefits.  Considering the distribution by crown projection area (cpa) 
            can reflect this potential difference.

            Crown projection area is calculated from the crown width measurements in the inventory as:
            
             cpa = 3.14*(crown width/2)^2
            
            Santamour's* often quoted "rule" of no more than 10% of the trees from one species, 
            no more than 20% from one genus and no more than 30% from one family is imperfect, but does provide some guidance with respect to "how much diversity is enough".
            With this in mind, look at the pie charts for frequency (number of trees) for species, genus and family by selectiong each of the radio buttons above to determine if
            some are over-planted.  This could help to guide planting recommendations. __Use caution when assessing filtered data!__
            
            In the following pie charts, "other" represents all species, genera or families not inccluded in the top ten making up the rest of the chart. 

            * Santamour, F.S. undated. Trees for urban planting: Diversity, uniformity, and common sense. 
            U.S. National Arboretum.  Washington D.C.).

        """)

    if divLevel == 'species':

        st.subheader('Remember, the diversity analysis at the species level will NOT include any trees identified only at the genus level (e.g. pinspp, mapspp,  etc.)')
        data = data.loc[(data.diversity_level == divLevel)]
    else:
        # data = data[data.diversity_level != divLevel]
        data = data.loc[(data.diversity_level != 'other')]
                   
    totalCount = len(data.index)
    topTenSpecies = data.loc[: , [divLevel, 'tree_name']]
    topTenSpeciesPT = pd.pivot_table(topTenSpecies, index=[divLevel], aggfunc='count')
    topTenSpeciesPT.reset_index(inplace=True)
    topTenSorted = topTenSpeciesPT.sort_values(by='tree_name',ascending=False).head(10)
    topTenTotal = topTenSorted['tree_name'].sum()
    otherTotal = totalCount - topTenTotal
    topTenPlusOther = topTenSorted.append({divLevel:'Other', 'tree_name': otherTotal}, ignore_index =True)
    topTenPlusOther.rename(columns = {'tree_name': 'frequency'},inplace = True)

    speciesPie = px.pie(topTenPlusOther, values='frequency', names = divLevel)
    speciesPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    speciesPie.update_layout(showlegend=False)
    
    
    TopTenTable = go.Figure(go.Table(
    header=dict(values=list(topTenPlusOther.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[topTenPlusOther[divLevel], topTenPlusOther.frequency],
                fill_color='lavender',
                align='left')))
    
    
    sppTable, sppChart =st.columns ((2,2))
    
    st.header('Tree Diversity Summary by Crown Projection Area')
    
    with sppTable:
        st.plotly_chart(TopTenTable)
    
    with sppChart:
        st.plotly_chart(speciesPie)
    
    totalCpa = data['cpa'].sum()
    
    topTenCpa = data.loc[: , [divLevel, 'cpa']]
    topTenCpaPT = pd.pivot_table(topTenCpa, index=[divLevel], aggfunc='sum')
    topTenCpaPT.reset_index(inplace=True)
    topTenCpaSorted = topTenCpaPT.sort_values(by='cpa',ascending=False).head(10)
    topTenCpaTotal = topTenCpaSorted['cpa'].sum()
    otherCpaTotal = totalCpa - topTenCpaTotal
    topTenCpaPlusOther = topTenCpaSorted.append({divLevel:'Other', 'cpa': otherCpaTotal}, ignore_index =True)
    topTenCpaPlusOther.rename(columns = {'cpa': 'Crown Projection Area'},inplace = True)
    
    CpaPie = px.pie(topTenCpaPlusOther, values='Crown Projection Area', names = divLevel)
    CpaPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    CpaPie.update_layout(showlegend=False)
    
    
    TopTenCpaTable = go.Figure(go.Table(
    header=dict(values=list(topTenCpaPlusOther.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[topTenCpaPlusOther[divLevel], topTenCpaPlusOther['Crown Projection Area']],
                fill_color='lavender',
                align='left')))
    
    
    sppTable, sppChart =st.columns ((2,2))
    
    with sppTable:
        st.plotly_chart(TopTenCpaTable)
    
    with sppChart:
        st.plotly_chart(CpaPie)
 
########################### Species origin analysis ###########################

def speciesOrigin(data):
        
    data = data.loc[data['diversity_level'] != 'other']
    
    originData = data.loc[: , ['seRegion', 'tree_name']]
    originPT = pd.pivot_table(originData, index='seRegion', aggfunc='count')
    originPT.reset_index(inplace=True)
    
    originPT.rename(columns = {'seRegion' : 'origin' , 'tree_name': 'frequency'},inplace = True)
    
    originPie = px.pie(originPT, values='frequency', names = 'origin')
    
    originPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    originPie.update_layout(showlegend=False)
    
    st.header('Tree Species Origin Summary')
    
    with st.expander("Click here to read an explanation of the Species Origin figure.", expanded=False):
        
            st.markdown('''This figure shows the proportion of the trees that are native to your region versus those 
                that have been introduced from outside the region.  This is based on the Ontario Tree Atlas that can be found at:
                https://www.ontario.ca/page/tree-atlas/.  This is more precise than simply stating if the species is native to 
                Ontario as is often done. This link shows you a map of the region and some information about each of the species native to the region
                '''
            )
    
    st.subheader('Remember, the species origin analysis will NOT include any trees identified only at the genus level (e.g. pinspp, mapspp,  etc.)')
    
    st.plotly_chart(originPie)
    
    st.markdown('___')


# def speciesOrigin(data):

#     data = data.loc[data['diversity_level'] != 'other']
    
#     originData = data.loc[: , ['native', 'tree_name']]
#     originPT = pd.pivot_table(originData, index='native', aggfunc='count')
#     originPT.reset_index(inplace=True)
    
#     originPT.rename(columns = {'native' : 'origin' , 'tree_name': 'frequency'},inplace = True)
    
#     originPie = px.pie(originPT, values='frequency', names = 'origin')
    
#     originPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
#     originPie.update_layout(showlegend=False)
    
#     st.header('Tree Species Origin Summary')
#     st.subheader('Remember, the species origin analysis will NOT include any trees identified only at the genus level (e.g. pinspp, mapspp,  etc.)')
    
#     st.plotly_chart(originPie)
    
#     st.markdown('___')

########################### Tree condition analysis###########################

def treeCondition(data):
    conditionData = data.loc[: , ['defects', 'tree_name']]
    conditionPT = pd.pivot_table(conditionData, index='defects', aggfunc='count')
    conditionPT.reset_index(inplace=True)
    
    conditionPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    conditionPie = px.pie(conditionPT, values='frequency', names = 'defects')
    
    conditionPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    conditionPie.update_layout(showlegend=False)
    
    st.header('Tree Condition Summary')
    st.plotly_chart(conditionPie)
    
    st.markdown('___')
    

########################### Relative DBH Analysis  ###########################

def relativeDBH(data):
    # st.markdown('___')
    try:
        with st.expander("Click here to read some comments about the DBH and Relative DBH analysis.", expanded=False):
        
            st.markdown("""Simply looking at the distribution of diameters at breast height (DBH) fails to tell the whole story since the urban forest is usually
                a mixture of species with large stature at maturity and those of small stature.  RDBH is derived by dividing each tree's DBH by the maximum DBH 
                for that species at maturity. We have derived the latter from the literature, municipal inventories and from our database of well over 150,000 trees collected 
                through Neighbour_woods_ inventories.
                
                __RDBH Class I__ represents all trees with a DBH 25% or less of the maximum DBH for the species (Target 40% );

                __RDBH Class II__ all trees with a DBH >25% or <50% of the maximum DBH for the species (Target 30%);

                __RDBH Class III__ all trees with a DBH >50% or <75% of the maximum DBH for the species (Target 20%); and

                __RDBH Class IV__ all trees with a DBH 75% or more, of the maximum DBH for the species (Target 10%).

                NOTE: This only includes trees that were identified to the species level and had a DBH recorded.  Not all species currently have a maximum DBH available.

                Targets are adapted from _Richards, N.A. 1983. Diversity and stability in a street tree population. Urban Ecology 7:159-171_.
            """)
        
        data = data.loc[data['diversity_level'] != 'other']
        data.dropna(subset=['dbh'], inplace = True)
        
        dbhData = data.loc[: , ['dbh_class', 'tree_name']]
        
        dbhPT = pd.pivot_table(dbhData, index='dbh_class', aggfunc='count')
        dbhPT.reset_index(inplace=True)
        dbhPT.rename(columns = {'dbh_class': 'DBH Class', 'tree_name': 'Frequency'},inplace = True)
        
        dbhNumberOfEntries = dbhPT['Frequency'].sum()
        
        dbhPT["Target"] = [dbhNumberOfEntries*0.4, dbhNumberOfEntries*0.3, dbhNumberOfEntries*0.2, dbhNumberOfEntries*0.1]
        
        dbhFig = go.Figure(data=[
            go.Bar(name='Current', x= dbhPT['DBH Class'], y=dbhPT['Frequency']),
            go.Bar(name='Target', x=dbhPT['DBH Class'], y=dbhPT['Target'])])

        dbhFig.update_layout(barmode='group', xaxis=dict(title_text='DBH CLass'), yaxis = dict(title_text='Frequency'))
        
        st.header("DBH Class Frequency")

        st.plotly_chart(dbhFig)



        realtiveDbhData = data.loc[: , ['rdbh_class', 'tree_name']]
        
        relativeDbhPT = pd.pivot_table(realtiveDbhData, index='rdbh_class', aggfunc='count')
        relativeDbhPT.reset_index(inplace=True)
        relativeDbhPT.rename(columns = {'rdbh_class': 'Relative DBH Class', 'tree_name': 'Frequency'},inplace = True)
        
        numberOfEntries = relativeDbhPT['Frequency'].sum()
        
        relativeDbhPT["Target"] = [numberOfEntries*0.4, numberOfEntries*0.3, numberOfEntries*0.2, numberOfEntries*0.1]
        
        rdbhFig = go.Figure(data=[
            go.Bar(name='Current', x= relativeDbhPT['Relative DBH Class'], y=relativeDbhPT['Frequency']),
            go.Bar(name='Target', x=relativeDbhPT['Relative DBH Class'], y=relativeDbhPT['Target'])])

        rdbhFig.update_layout(barmode='group', xaxis=dict(title_text='Relative DBH CLass'), yaxis = dict(title_text='Frequency'))
        
        st.header("Relative DBH Class Frequency")

        st.plotly_chart(rdbhFig)

    except ValueError:
        st.warning("Complete the filter and press enter")    

    st.markdown('___')


########################### Species Suitability Analysis ###########################

def speciesSuitablity(data):
    
    try:
        
        data = data.loc[data['diversity_level'] != 'other']
        suitabilityData = data.loc[: , ['suitability', 'tree_name']]
        suitabilityPT = pd.pivot_table(suitabilityData, index='suitability', aggfunc='count')
        suitabilityPT.reset_index(inplace=True)
        suitabilityPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
        suitabilityPie = px.pie(suitabilityPT, values='frequency', names = 'suitability')
        suitabilityPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
        suitabilityPie.update_layout(showlegend=False)
        
        st.header('Tree Species Suitability Summary')
        with st.expander("Click here to read about species suuitability", expanded=False):
            st.markdown('''Tree species suitability is based on an expert opinion survey conducted by ISA Ontario during the development of
            the Supplement to the Council of Tree and Landscape Appraiser's Guide to tree appraisal 10 edition.  The survey asked experts across Ontario 
            to rate a list of commonly planted species on a series of criteria.  Each species was given a numerical score.  We converted these scores to categories of
            Very Poor (score < 0.5), Poor (0.51 < 0.6), Good (0.61 to 0.7 and Excellent (>0.70)).  Unfortunately, the scoring process carried out by the expert
            panel did NOT include the tendency for a species to be invasive.  We adapted our ranking so that any species considered to be invasive in Ontario 
            would be considered to have a suitability of Very Poor.  See the section below for more details on invasivity. ''')

        
        
        st.plotly_chart(suitabilityPie)

        
        invasivityData = data.loc[: , ['invasivity', 'tree_name']]
        invasivityPT = pd.pivot_table(invasivityData, index='invasivity', aggfunc='count')
        invasivityPT.reset_index(inplace=True)
        invasivityPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
        invasivityPie = px.pie(invasivityPT, values='frequency', names = 'invasivity')
        invasivityPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
        invasivityPie.update_layout(showlegend=False)
        
        st.header('Tree Species Invasivity Summary')
        
        with st.expander("Click heree to read about species invasivity", expanded=False):
            st.markdown('''The tree species indicated as invasive are based on data shown in https://www.eddmaps.org/ontario/species/''')

        st.plotly_chart(invasivityPie)

    except ValueError:
        st.warning("You must complete the selection in the filtering section of the sidebar.")    
    st.markdown('___')

######################################################################################
if fileName is not None:
    setupSidebar(df)


