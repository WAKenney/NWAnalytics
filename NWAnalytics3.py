# -*- coding: utf-8 -*-
"""
Re-Created on 15/02/20

@author: W.A. Kenney
"""

import base64
import io
from logging import _STYLES
from math import isnan
from os import name
from tokenize import Name
import folium

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



st.set_page_config(layout="centered")

# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)
# st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

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

with st.expander("Click here for help in getting started.", expanded=False):
    st.markdown("""
        Neighbourwoods is a community-based program to assist community groups in the stewardship of the urban forest in their neighbourhood.
        Using NWAnalytics, you can map and analyze various aspects of the urban forest that will help you develop and implement stewardship strategies.
        At present, you must first have your Neighbourwoods tree inventory data in a Neighbourwoods MS excel workbook (version 2.6 or greater).

        To get started, select your Neighbourwoods MS excel workbook at the sidebar on the left. Once your data has been uploaded (this may take 
        a few minutes if you have a big file, be patient) you will be asked to select the functions you want to display.  Select as many as you 
        want from the dropdown list __AND CLICK ON CONTINUE__.  The selected analyses will be shown in the main frame.

        You can conduct these analyses on all the data, or you can filter the data for specific queries. The table below shows your inventory data 
        and can be filtered much as you would a Microsoft Excel worksheet.  Scroll across the columns and place your cursor on the header of the
        column that you wish to filter.  As you do so, an icon of three lines will appear in the header, click on this icon.  The type of filter
        will depend on the type of data in that column.  For text data, you will see a list of all the options in that column with a checkbox to the left of each line.  To filter 
        out specific items first click on the check box beside _Select All_ to switch off all the items.  Now, click on the box(es) beside the items
        you want in your filter.  Note that you can type in an item name to shorten the list.  Once you have selected everything you want in the
        filter, you must click on the _Update_ button at the top left of the table.  Your filtered data will now be used in all the functions you select
        from the sidebar at the left.  For numerical data you will have the option to filter using comparison types such as equal to, greater than, etc.
        Remember to click on the _Update_ button to commit your filter to the analysis functions.

        You must clear the filters manually by going to each column header with a filter and either click on _Select all_ or remove the values 
        from the boxes in a numeric filter.  Columns with an active filter will have an icon that looks like a funnel in the header.

        Note that you can save your filtered data as an Excel workbook by clicking on the link at the bottom of the data table.

        In various places you will have opportunities to click on a box for more information, just as you are reading this text.  To close these boxes, 
        simply click on the header button again.

        Click on the following link to read more about Neighbourwoods: http://neighbourwoods.org/')

        For support, contact Andy Kenney at:     a.kenney@utoronto.ca
""")

st.markdown("___")

mainScreen =st.empty()
filterResultHeader = st.empty()
getFileScreen = st.sidebar.empty()


def aggFilter(df):

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_default_column(editable=True, filter=True)

    gb.configure_column(field='tree_name', header_name='Tree Name')
    gb.configure_column(field='description', header_name='Tree Description',
        editable=False, filter = False, wrapText=True, autoHeight = True)
    gb.configure_column(field='latitude', hide = True)
    gb.configure_column(field='longitude', hide = True)
    gb.configure_column(field='date', editable=True)
    
    gb.configure_column(field='species', editable=True)
    gb.configure_column(field='street', editable=True)
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

    originalSize = len(df.index)
    filteredSize = len(gridReturn['data'].index)
    if filteredSize<originalSize:
        st.subheader("NOTE: You are using filtered data.")

    return gridReturn['data']

fileName ='empty'

df = pd.DataFrame()

fileName = getFileScreen.file_uploader("Browse for or drag and drop the name of your Neighburwoods MS excel workbook", 
    type = ['xlsm', 'xlsx'], 
    key ='fileNameKey')

@st.experimental_memo(show_spinner=False)
def getData(fileName):

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

if fileName is not None:

    with st.spinner(text = 'Setting up your data, please wait...'):
        df = getData(fileName)[0]
        speciesTable = getData(fileName)[1]
        colorsTable = getData(fileName)[2]
        colorsDict = colorsTable.to_dict('dict')['color']
        
        select_df = aggFilter(df)


def setupSidebar(df):
    """
    This def sets up the Streamlit sidebar
    """ 
    # getFileScreen.empty()

    selectFunctionForm = st.sidebar.form(key = 'selectFunction')
    selectFunctionForm.header('Select the function(s) you want to display ')
    selectFunction = selectFunctionForm.multiselect('',['Map Trees', 'Tree Diversity', 'Species Origin', 'Tree Condition', 'Relative DBH', 'Suitability & Invasivity'])
    selectFunctionForm.form_submit_button("Continue")

    # st.sidebar.header("Do you want to FILTER the tree data?")
    # filterMenu1 = st.sidebar.empty()
    # with filterMenu1:
        
    #     filtYesOrNo = st.radio("", options =('No, use all the data', 'Yes, filter the data'))

    # if filtYesOrNo == 'Yes, filter the data':
        
    #     filterMenu2 = st.sidebar.empty()
        
    #     with filterMenu2:         
    #         filterType = st.radio("Select the type of filter you want to use", options =('Filter by List?', 'One Parameter Filter?', 'Two Parameter Filter?'))
            
    #     if filterType == 'Filter by List?':
    #         select_df = simpleFilter(df)
            
    #     elif filterType == 'One Parameter Filter?':
    #         select_df = oneParameterFilter(df, 0)
        
    #     else:
    #         select_df = twoParameterFilter(df)
                    
    # else:  #Don't filter
    #     select_df = df

    # if 'Show Data' in selectFunction:
    #     showTable(select_df)
        
    if 'Map Trees' in selectFunction:
        # mapIt(select_df)
        mapItFolium(select_df)
        # mapIt2(select_df)

    if 'Tree Diversity' in selectFunction:
        diversity(select_df)    

    if 'Species Origin' in selectFunction:
        speciesOrigin(select_df)

    if 'Tree Condition' in selectFunction:
        treeCondition(select_df)
        
    if 'Relative DBH' in selectFunction:
        relativeDBH(select_df)

    if 'Suitability & Invasivity' in selectFunction:
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

    st.header('Show the inventory data')


    with st.expander("Click here to read an explanation of the Show Data function.", expanded=False):
        
            st.markdown('''This function displays the Neighbourwoods inventory data, either filtered or not filtered, as a table. You can add columns to 
            the default _Description_ and _Tree Name_ columns, and change the width of the columns using a slider.  You can also save the data as an Excel file which you can 
            read and manipulate as you want in your favourite spreadsheet software.  The exported worksheet will have ALL the columns regardless of which 
            columns were added to the NWAnalytics table.  If you have filtered the data in NWAnalytics, only the filtered data will be exported.
                '''
            )
        
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

    

def mapItFolium(mapData):

    # mapCol1, mapCol2, mapCol3 = st.columns(3)
    pointSizeSlider = st.slider('Move the slider to adjust the point size', min_value = 2, max_value = 20, value =4)
        
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
        radius= pointSizeSlider,
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
    

######################################################
def mapIt(mapData):

    with st.spinner(text = 'Please wait while your map is set up...'):

        if mapData.empty:
            st.warning("Be sure to finish selecting the filtering values in the sidebar to the left.")
            
        avLat = mapData['latitude'].mean()  #calculate the average Latitude value and average Longitude value to use to centre the map
        avLon = mapData['longitude'].mean()
        
        mapData['condColor'] = mapData['defects'].map(codes) # create a column called conColor and map the color values based on 
                                                                    #the condition code in the dictionary called condColor
        
        map_df = mapData[mapData['latitude'].notna()] # Drop entries with no latitude or longitude values entered
        map_df = mapData[mapData['longitude'].notna()]
                
        fig = px.scatter_mapbox(data_frame = map_df, lat="latitude", lon="longitude", 
                                hover_name='tree_name',
                                hover_data={"tree_name": False,
                                            "description": True,
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
        
        st.plotly_chart(fig)
        
        return fig


# ########################################## Diversity ############################################
    
def diversity(data):

    data = data.loc[data['diversity_level'] != 'other']
   
    divLevel = st.radio('Select a level of diversity', ('species', 'genus', 'family'))
    
    st.header('Tree diversity summary by ' + divLevel)

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

    st.subheader('Diversity based on the number of trees (frequency)')

    if divLevel == 'species':

        st.write('Remember, the diversity analysis at the species level will NOT include any trees identified only at the genus level (e.g. pinspp, mapspp,  etc.)')
        richness =data.species.nunique()
        st.write('Keeping the above in mind, there are ', richness, 'unique species (species richness).')

        data = data.loc[(data.diversity_level == divLevel)]
    else:
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
    # topTenPlusOther = pd.merge(topTenPlusOther, speciesTable[['species', 'color', 'species_code']], on="species", how="left", sort=False)

    # topTenPlusOther.loc[topTenPlusOther['species'] == 'Other', 'color'] = 'gray'
    
    speciesPie = px.pie(topTenPlusOther, 
        values='frequency', 
        # names = 'species',
        # color= 'species',
        names = divLevel,
        color = divLevel,
        color_discrete_map = colorsDict
        )

    speciesPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    speciesPie.update_layout(showlegend=False)
    speciesPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(speciesPie)
    
    st.subheader('Diversity based on crown projection area (CPA)')
    
    totalCpa = data['cpa'].sum()
    
    topTenCpa = data.loc[: , [divLevel, 'cpa']]
    topTenCpaPT = pd.pivot_table(topTenCpa, index=[divLevel], aggfunc='sum')
    topTenCpaPT.reset_index(inplace=True)
    topTenCpaSorted = topTenCpaPT.sort_values(by='cpa',ascending=False).head(10)
    topTenCpaTotal = topTenCpaSorted['cpa'].sum()
    otherCpaTotal = totalCpa - topTenCpaTotal
    topTenCpaPlusOther = topTenCpaSorted.append({divLevel:'Other', 'cpa': otherCpaTotal}, ignore_index =True)
    topTenCpaPlusOther.rename(columns = {'cpa': 'Crown Projection Area'},inplace = True)
    # topTenCpaPlusOther = pd.merge(topTenCpaPlusOther, speciesTable[['species', 'color', 'species_code']], on="species", how="left", sort=False)
    
    CpaPie = px.pie(topTenCpaPlusOther, 
        values='Crown Projection Area', 
        # names = 'species',
        # color='species',
        names = divLevel,
        color = divLevel,
        color_discrete_map = colorsDict
        )

    CpaPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    CpaPie.update_layout(showlegend=False)
    CpaPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(CpaPie)
    
########################### Species origin analysis ###########################

def speciesOrigin(data):
        
    data = data.loc[data['diversity_level'] != 'other']

    st.header('Tree Species Origin Summary')
    
    with st.expander("Click here to read an explanation of the Species Origin figure.", expanded=False):
        
            st.markdown('''These figures show the proportion of the trees that are native to your region versus those 
                that have been introduced from outside the region.  This is based a series of maps documented in 
                the "Atlas of United States Trees" by Elbert L. Little, Jr.
                Digital versions of the maps for tree species that naturally occur in Ontario (according to Little) 
                were downloaded.  These maps were overlaid (in a GIS) on digital maps of the Ecoregions of Ontario.  
                Any species for which the map overlaid any given Ecoregion by more than 5% of the area of the Ecoregion 
                was considered to be "native" to that Ecoregion. Otherwise, the species was considered to be introduced.
                This approach is much more precise than simply stating if the species is native to Ontario, as is often done. [More information about Little's maps can be found here ](https://web.archive.org/web/20170127093428/https://gec.cr.usgs.gov/data/little/)
                and [the Ecoregions map can be viewed here ](https://geohub.lio.gov.on.ca/datasets/ecoregion/explore?location=42.987702%2C-66.706064%2C8.53)
                
                '''
            )
    
    st.write('Remember, the species origin analysis will NOT include any trees identified only at the genus level (e.g. pinspp, mapspp,  etc.)')
    
    # By frequency

    st.subheader("Origin by the number of trees (frequency)")

    originData = data.loc[: , ['seRegion', 'tree_name']]
    originPT = pd.pivot_table(originData, index='seRegion', aggfunc='count')
    originPT.reset_index(inplace=True)
    
    originPT.rename(columns = {'seRegion' : 'origin' , 'tree_name': 'frequency'},inplace = True)
    
    originPie = px.pie(originPT, values='frequency', names = 'origin')
    
    originPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    originPie.update_layout(showlegend=False)
    originPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(originPie)

    # By CPA

    st.subheader("Origin by crown projection area (cpa)")

    originDataCPA = data.loc[: , ['seRegion', 'cpa']]

    originPTCPA = pd.pivot_table(originDataCPA, index='seRegion', aggfunc='sum')
       
    originPTCPA.reset_index(inplace=True)
    
    originPTCPA.rename(columns = {'seRegion' : 'origin'},inplace = True)
    
    originPieCPA = px.pie(originPTCPA, values='cpa', names = 'origin')
    
    originPieCPA.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    originPieCPA.update_layout(showlegend=False)
    originPieCPA.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(originPieCPA)
    
########################### Tree condition analysis###########################

def treeCondition(data):

    st.header('Tree Condition Summary')

    conditionData = data.loc[: , ['defects', 'tree_name']]
    conditionPT = pd.pivot_table(conditionData, index='defects', aggfunc='count')
    conditionPT.reset_index(inplace=True)
    
    conditionPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    conditionPie = px.pie(conditionPT, values='frequency', names = 'defects')
    
    conditionPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    conditionPie.update_layout(showlegend=False)
    conditionPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.subheader("Condition by the number of trees (frequency)")
    st.plotly_chart(conditionPie)



    conditionDataCPA = data.loc[: , ['defects', 'cpa']]
    conditionPTCPA = pd.pivot_table(conditionDataCPA, index='defects', aggfunc='sum')
    conditionPTCPA.reset_index(inplace=True)
    
    # conditionPTCPA.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    conditionPieCPA = px.pie(conditionPTCPA, values='cpa', names = 'defects')
    
    conditionPieCPA.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    conditionPieCPA.update_layout(showlegend=False)
    conditionPieCPA.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    

    st.subheader("Condition by Crown Projection Area (cpa)")
    st.plotly_chart(conditionPieCPA)
    
########################### Relative DBH Analysis  ###########################

def relativeDBH(data):

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


########################### Species Suitability Analysis ###########################

def speciesSuitablity(data):

    st.header('Tree Species Suitability Summary')
    
    with st.expander("Click here to read about species suitability", expanded=False):
    
        st.markdown('''Tree species suitability is based on an expert opinion survey conducted by ISA Ontario during the development of
        the Supplement to the Council of Tree and Landscape Appraiser's Guide to tree appraisal 10 edition.  The survey asked experts across Ontario 
        to rate a list of commonly planted species on a series of criteria.  Each species was given a numerical score.  We converted these scores to categories of
        Very Poor (score < 0.5), Poor (0.51 < 0.6), Good (0.61 to 0.7 and Excellent (>0.70)).  Unfortunately, the scoring process carried out by the expert
        panel did NOT include the tendency for a species to be invasive.  We adapted our ranking so that any species considered to be invasive in Ontario 
        would be considered to have a suitability of Very Poor.  See the section below for more details on invasivity. ''')
    
    st.subheader('Suitability by number of trees (frequency)')

    data = data.loc[data['diversity_level'] != 'other']
    
    suitabilityData = data.loc[: , ['suitability', 'tree_name']]
    suitabilityPT = pd.pivot_table(suitabilityData, index='suitability', aggfunc='count')
    suitabilityPT.reset_index(inplace=True)
    suitabilityPT.rename(columns = {'tree_name': 'frequency'},inplace = True)

    suitabilityPie = px.pie(suitabilityPT, values='frequency', names = 'suitability',
        color = 'suitability',
        color_discrete_map={'Excellent':'darkgreen',
                                'Good':'springgreen',
                                'Poor':'palegreen',
                                'Very Poor':'yellow'})
    suitabilityPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    suitabilityPie.update_layout(showlegend=False)
    suitabilityPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    

    st.plotly_chart(suitabilityPie)


    st.subheader('Suitability by crown projection area (cpa)')

    suitabilityDataCPA = data.loc[: , ['suitability', 'cpa']]
    suitabilityPTCPA = pd.pivot_table(suitabilityDataCPA, index='suitability', aggfunc='sum')
    suitabilityPTCPA.reset_index(inplace=True)
    # suitabilityPTCPA.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    suitabilityPieCPA = px.pie(suitabilityPTCPA, values='cpa', names = 'suitability',
        color = 'suitability',
        color_discrete_map={'Excellent':'darkgreen',
                                'Good':'springgreen',
                                'Poor':'palegreen',
                                'Very Poor':'yellow'})

    suitabilityPieCPA.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    suitabilityPieCPA.update_layout(showlegend=False)
    suitabilityPieCPA.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    

    st.plotly_chart(suitabilityPieCPA)

    st.header('Tree Species Invasivity Summary')
    
    with st.expander("Click here to read about species invasivity", expanded=False):
        st.markdown('''The tree species indicated as invasive are based on data shown in https://www.eddmaps.org/ontario/species/''')

    st.subheader('Invasivity by the number of trees (frequency)')

    invasivityData = data.loc[: , ['invasivity', 'tree_name']]
    invasivityPT = pd.pivot_table(invasivityData, index='invasivity', aggfunc='count')
    invasivityPT.reset_index(inplace=True)
    invasivityPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    invasivityPie = px.pie(invasivityPT, values='frequency', names = 'invasivity',
        color = 'invasivity',
        color_discrete_map={'invasive':'yellow',
                                'non-invasive':'darkgreen'})
    
    invasivityPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    invasivityPie.update_layout(showlegend=False)
    invasivityPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    
    st.plotly_chart(invasivityPie)

    st.subheader('Invasivity by crown projection area (cpa)')

    invasivityDataCPA = data.loc[: , ['invasivity', 'cpa']]
    invasivityPTCPA = pd.pivot_table(invasivityDataCPA, index='invasivity', aggfunc='sum')
    invasivityPTCPA.reset_index(inplace=True)
    # invasivityPT.rename(columns = {'tree_name': 'frequency'},inplace = True)
    
    invasivityPieCPA = px.pie(invasivityPTCPA, values='cpa', names = 'invasivity',
        color = 'invasivity',
        color_discrete_map={'invasive':'yellow',
                                'non-invasive':'darkgreen'})
    
    invasivityPieCPA.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    invasivityPieCPA.update_layout(showlegend=False)
    invasivityPieCPA.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    
    st.plotly_chart(invasivityPieCPA)

######################################################################################
if fileName is not None:
    setupSidebar(df)

    


