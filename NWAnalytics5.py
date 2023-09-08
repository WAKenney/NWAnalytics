# -*- coding: utf-8 -*-
"""
Re-Created on 14/03/2022

@author: W.A. Kenney

NWAnalytics5
"""

from ast import Break, NotIn
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode

import base64
from dataclasses import dataclass
import io
import numpy as np
import folium
import geopandas as gpd
import os
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import streamlit as st
from datetime import date
from folium.plugins import FloatImage
from folium.plugins import Fullscreen
from PIL import Image
# from streamlit.state.session_state import SessionState
from streamlit_folium import folium_static
from geopandas import GeoDataFrame


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

currentDir = "https://raw.githubusercontent.com/WAKenney/NWAnalytics/master/"

# colTitles=['tree_name', 'species', 'genus', 'family', 'street', 'address', 'location_code', 'ownership_code', 'number_of_stems', 'dbh',
#     'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'reduced_crown', 'unbalanced_crown', 'defoliation',
#     'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean', 'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks',
#     'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space','crack', 'girdling_roots', 'exposed_roots', 'recent_trenching', 'cable_or_brace',
#     'wire_conflict', 'sidewalk_conflict', 'structure_conflict', 'tree_conflict', 'sign_conflict', 'comments', 'demerits',
#     'simple_rating', 'cpa', 'rdbh', 'rdbh_class', 'dbh_class', 'native', 'suitability', 'defects', 'invasivity', 'seRegion']
    
condColumns = ['reduced_crown', 'unbalanced_crown', 'defoliation', 'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean',
    'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space',
    'crack', 'girdling_roots', 'exposed_roots', 'recent_trenching']  # Thisis used in the tree condition function to loop through these columns

# desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') # Get thelocation of the Desktop for temporary file storage

titleCol1, titleCol2, titleCol3 =st.columns((1,4,1))
title = currentDir + 'NWAnalyticsTitle.jpg'
titleCol2.image(title, use_column_width=True)
titleCol1.write("Sept 8 2023")

with st.expander("Click here for help in getting started.", expanded=False):
    st.markdown("""
        Neighbourwoods is a community-based program to assist community groups in the stewardship of the urban forest in their neighbourhood.
        Using NWAnalytics, you can map and analyze various aspects of the urban forest that will help you develop and implement stewardship strategies.
        At present, you must first have your Neighbourwoods tree inventory data in a Neighbourwoods MS excel workbook (version 2.6 or greater).

        To get started, select your Neighbourwoods MS excel workbook at the sidebar on the left. Once your data has been uploaded (this may take 
        a few minutes if you have a big file, be patient) you will be asked to select the functions you want to display.  Select as many as you 
        want from the dropdown list __AND CLICK ON CONTINUE__.  The selected analyses will be shown in the main frame.

        You can conduct these analyses on all the data, or you can filter the data for specific queries. For hints on filtering your data, click on the button below.

        In various places you will have opportunities to click on a box 
        for more information, just as you are reading this text.  To close these boxes, simply click on the header button again.

        Click on the following link to read more about Neighbourwoods: http://neighbourwoods.org/')

        For support, contact Andy Kenney at:     a.kenney@utoronto.ca
""")

st.markdown("___")

getFileScreen = st.sidebar.empty()


def aggFilter(agData):
    
    """ This function sets up the grid to view and filter the data"""
    
    df = agData.copy()

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_default_column(editable=True, filter=True)

    # gb.configure_column(field='tree_name', header_name='Tree Name')
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
    # gb.configure_column(field='demerits', hide = True)
    gb.configure_column(field='seRegion', header_name='Origin')
    gb.configure_column(field='structural', header_name='Structural Defect(s)')
    gb.configure_column(field='health', header_name='Health Defect(s)')
    gb.configure_column(field='defects', header_name='Defect Summary')
    gb.configure_column(field='color', hide = True)

    gridOptions = gb.build()

    gridReturn = AgGrid(df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        height = 500, 
        theme = 'streamlit',
        enable_enterprise_modules=True, # enables right click and fancy features - can add license key as another parameter (license_key='string') if you have one
        key='select_grid', # stops grid from re-initialising every time the script is run
        reload_data=True, # allows modifications to loaded_data to update this same grid entity
        update_mode=GridUpdateMode.MANUAL,
        data_return_mode="FILTERED_AND_SORTED")

    gridReturnData = gridReturn['data']

###########################
    # # This provides the option to save the filtered data to a spreadsheet
    # towrite = io.BytesIO()
    # downloaded_file = gridReturn['data'].to_excel(towrite, encoding='utf-8', index=False, header=True, sheet_name = 'summary')
    # towrite.seek(0)  # reset pointer
    # b64 = base64.b64encode(towrite.read()).decode()  # some strings
    # linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="NwAnalyticsData.xlsx">Click here to save your data as an Excel file</a>'
    # st.markdown(linko, unsafe_allow_html=True)
##############################


    # Test to see if working with full dataset (originalSize) or a filtered subset (filteredSize)
    filteredData = gridReturnData.copy()
    filteredData.drop(['defectColour', 'color', 'geometry'], axis =1, inplace = True)
    
    originalSize = len(df.index)
    filteredSize = len(gridReturn['data'].index)

    if filteredSize<originalSize:
        st.warning(f"__NOTE__: You are using filtered data with {filteredSize} entries selected.  All functions will now operate on this filtered data. Click on UPDATE at the top left of the table above when you want to use the full (unfiltered) dataset.")
        st.experimental_data_editor(filteredData)

        # filterViewYesNo = st.button("Click here to save a table of the filtered data")
        # if filterViewYesNo:
            
    #    This saves the filtered data to a spreadsheet
        towrite = io.BytesIO()
        downloaded_file = filteredData.to_excel(towrite, encoding='utf-8', index=False, header=True, sheet_name = 'Filtered Data')
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode()  # some strings
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="FilteredData.xlsx">Click here to save your FILTERED data as an Excel file</a>'
        st.markdown(linko, unsafe_allow_html=True)
        
    # if filteredSize<originalSize:
    #     st.warning(f"__NOTE__: You are using filtered data with {filteredSize} entries selected.  All functions will now operate on this filtered data. Click on UPDATE at the top left of the table above when you want to use the full (unfiltered) dataset.")

    #     filterViewYesNo = st.button("Click here to view and save a table of the filtered data")
    #     if filterViewYesNo:
    #         filteredData = gridReturnData.copy()
    #         # filteredData.drop(['defectColour', 'color', 'geometry'], axis =1, inplace = True) 
    #         st.experimental_data_editor(filteredData)

    #     #    This provides the option to save the filtered data to a spreadsheet
    #         towrite = io.BytesIO()
    #         downloaded_file = filteredData.to_excel(towrite, encoding='utf-8', index=False, header=True, sheet_name = 'Filtered Data')
    #         towrite.seek(0)  # reset pointer
    #         b64 = base64.b64encode(towrite.read()).decode()  # some strings
    #         linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="FilteredData.xlsx">Click here to save your data as an Excel file</a>'
    #         st.markdown(linko, unsafe_allow_html=True)

    return gridReturnData

fileName ='empty'

df = pd.DataFrame()

fileName = getFileScreen.file_uploader("Browse for or drag and drop the name of your Neighbourwoods SUMMAY file here", 
    type = ['xlsm', 'xlsx'], 
    key ='fileNameKey')

@st.cache_data(show_spinner=False)
def getData(fileName):
    """Import tree data and species table and do some data organization"""

    if fileName is not None:
        df = pd.read_excel(fileName, sheet_name = "summary", header = 0)


    #read the species table from the current directory which should be Github repo
    speciesFile = currentDir + 'NWspecies220522.xlsx' 
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
                                'Invasivity':'invasivity', 'Diversity Level':'diversity_level',
                                'DBH Class':'dbh_class','Native':'native','Species Suitability':'suitability','Structural Defect':'structural', 
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

    df['defects'] = df.apply(defect_setup, axis = 1) #Apply the defect_setup fucntion to all rows of the trees dataframe
    
    def setDefectColour(df):
        ''' sets a colour name in column defectColour based on the value in column defects.  This is for mapping'''
        
        if df['defects'] == 'No major defects':
            return 'darkgreen'

        elif df['defects'] == 'Major structural defect(s)':
            return 'yellow'
        
        elif df['defects'] == 'Major health defect(s)':
            return 'greenyellow'

        elif df['defects'] == 'Major structural AND health defect(s)':
            return 'red'
        
        else:
            return 'black'

    # Apply defectColour function to all rows of the trees dataframe
    df['defectColour'] = df.apply(setDefectColour, axis = 1) 

    #Read variables from the speices table and add them to the trees table
    # df = pd.merge(df, speciesTable[['species', 'seRegion']], on="species", how="left", sort=False)
    # df = pd.merge(df, speciesTable[['species', 'color']], on="species", how="left", sort=False)
    df = pd.merge(df, speciesTable[['species', 'color', 'seRegion']], on="species", how="left", sort=False)

    #Record a suitability of very poor for any species that is invasive based on the species table
    df.loc[(df.invasivity =='invasive'), 'suitability'] = 'very poor'

    df.merge(speciesTable, how = 'left', on = 'species', sort = False )

    # save the 'data' pandas dataframe as a geodataframe
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude)).copy() 
 
    # Save the inventory dates as a string.  Otherwise an error is thrown when mapping
    df['date'] = df['date'].astype(str)

    # get the species specific colour from the species table for each entry and create the coloursTable
    colorsTable = pd.read_excel(speciesFile,sheet_name = "colors")
    colorsTable.set_index('taxon', inplace = True)

    return [df, speciesTable, colorsTable]



if fileName is not None:

    with st.spinner(text = 'Setting up your data, please wait...'):
        df = getData(fileName)[0]

        speciesTable = getData(fileName)[1]
        colorsTable = getData(fileName)[2]
        colorsDict = colorsTable.to_dict('dict')['color']

        with st.expander("Click here for hints on filtering your data", expanded=False):
            st.markdown("""The table below shows your inventory data 
        and can be filtered much as you would a Microsoft Excel worksheet.  Scroll across the columns and place your cursor on the header of the
        column that you wish to filter.  As you do so, an icon of three lines will appear in the header, click on this icon.  The type of filter
        will depend on the type of data in that column.  For text data, you will see a list of all the options in that column with a checkbox to the left of each line.  To filter 
        out specific items first click on the check box beside _Select All_ to switch off all the items.  Now, click on the box(es) beside the items
        you want in your filter.  Note that you can type in an item name to shorten the list.  ***Once you have selected everything you want in the
        filter, you must click on the Update button at the top left of the table***.  Your filtered data will now be used in all the functions you select
        from the sidebar at the left.
        For numerical data you will have the option to filter using comparison types such as equal to, greater than, etc.
        Remember to click on the _Update_ button to commit your filter to the analysis functions. 
        Columns with an active filter will have an icon that looks like a funnel in the header.        
        To clear all filters and return to the full data set, click on the Update button.
        Note: that you can save your filtered data as an Excel workbook by clicking on the link at the bottom of the FILTERED data table.""")
        

        # display the selected data (select_df) using AgGrid
        
        select_df = aggFilter(df)
        
def checkData(chkData):

    with st.spinner(text = 'Checking your data, please wait...'):

        # Older versions of the data didn't include surface roots.  To avoid crashing the app, this function checks to see if surface roots are in the data.
        # If not, then this attribute is removed from the list of column names (cols)

        df = chkData.copy()

        if df['exposed_roots'].isnull().all():

            cols = ['tree_name','latitude', 'longitude', 'block', 'species', 'street', 'address', 'location_code', 'ownership_code', 'number_of_stems', 'dbh',
            'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'reduced_crown', 'unbalanced_crown', 'defoliation',
            'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean', 'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks',
            'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space','crack', 'girdling_roots', 'recent_trenching', 'cable_or_brace',
            'wire_conflict', 'sidewalk_conflict', 'structure_conflict', 'tree_conflict', 'sign_conflict']

            st.write('It appears that you did not record exposed roots for any entries.  This attribute will be ignored in the "check data" function.')

        else:
            cols = ['tree_name','latitude', 'longitude', 'block', 'species', 'street', 'address', 'location_code', 'ownership_code', 'number_of_stems', 'dbh',
            'hard_surface', 'crown_width', 'height_to_crown_base', 'total_height', 'reduced_crown', 'unbalanced_crown', 'defoliation',
            'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean', 'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'conks',
            'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space','crack', 'girdling_roots', 'exposed_roots', 'recent_trenching', 'cable_or_brace',
            'wire_conflict', 'sidewalk_conflict', 'structure_conflict', 'tree_conflict', 'sign_conflict']

        # Conks is the only attibute with values of 0 or 1 so a species list of column names EXCLUDING conks is set up called 'conditionColsNoConks'

        conditionColsNoConks = ['reduced_crown', 'unbalanced_crown', 'defoliation', 'weak_or_yellow_foliage', 'dead_or_broken_branch', 'lean',
                    'poor_branch_attachment', 'branch_scars', 'trunk_scars', 'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space',
                    'crack', 'girdling_roots', 'exposed_roots', 'recent_trenching']

        nonTrees = ['dead tree', 'forest', 'hedge','plantable spot', 'snag', 'stump']

        trees = df['tree_name']
       
       #don't need these columnns since they are derived values
        df.drop(['genus', 'family','cpa', 'rdbh', 'rdbh_class', 'dbh_class', 'native', 'color', 'health','structural', 'defects', 'defectColour', 'diversity_level', 'invasivity',
            'comments', 'suitability', 'seRegion', 'description', 'geometry'], 
            axis=1, inplace=True) 
        
        # Demerits and simple_rating are columns in the legacy format of Neighbourwoods MS 2.6.  If they are present they will be dropped
        if "demerits" in df.columns:
            df.drop(['demerits'])
        if "simple_rating" in df.columns:
            df.drop(['simple_rating'])

        # Make the index tree_name so the df.at function can be used later on
        df.set_index('tree_name', drop = False,  inplace = True) 

        # add a column to df called error and fill all with ok.  The ok is replaced by error message later on
        df['error'] = 'ok' 

        # add a column to df called warning and fill all with ok.  The ok is replaced by warning message later on
        df['warning'] = 'ok'

        # Check if there is a missing value in all columns except for dead, plantable spots etc.  Message is added to the column warnng in df
        
        # Check for duplicate tree names.  If so print a warning
        dupTest = df['tree_name'].duplicated(keep = 'first')
        dup = dupTest[dupTest].index

        if dupTest.values.sum() >= 1:

            st.error('''Uh Oh!  The following tree(s) have duplicate names.  Exit this app, 
            correct any errors in your data input file then re-start this app, re-load the corrected file and proceed.''')
            
            st.write(dup)

        else:
            
            for tree in trees:

                sppName = df.at[tree, 'species']

                if  df.at[tree, 'species'] not in nonTrees:

                    for col in cols:
                        
                        wMessage = df.at[tree, 'warning']

                        if pd.isna(df.at[tree, col]):

                            if df.at[tree, 'warning'] == 'ok':

                                df.at[tree, 'warning'] = 'missing ' + col

                            else:
                                
                                df.at[tree, 'warning'] = wMessage + '; missing ' + col


        # Check for invalide codes in the tree condition columns.  Must be either 0, 1, 2, or 3.  Using tree names of entries exclusing nontrees like dead, forest, hedge, etc.
        
        for col in conditionColsNoConks:
                
            wMessage = df.at[tree, 'error']

            if df.at[tree, col] not in [0, 1, 2, 3]:

                if df.at[tree, 'error'] == 'ok':

                    df.at[tree, 'error'] = 'invalide code in ' + col

                else:
                    
                    df.at[tree, 'error'] = wMessage + '; invalide code in ' + col

                    
        #check for invalide codes for conks.  This is done separately because conks only have codes of 0 or 1            
        wMessage = df.at[tree, 'error']

        if df.at[tree, 'conks'] not in [0, 1]:

            if df.at[tree, 'error'] == 'ok':

                df.at[tree, 'error'] = 'Invalide code in conks'

            else:
                
                df.at[tree, 'error'] = wMessage + '; invalide code in conks'

        #check for invalide codes for ownership.            
        wMessage = df.at[tree, 'error']

        if df.at[tree, 'ownership_code'] not in ['c', 'p', 'j']:

            if df.at[tree, 'error'] == 'ok':

                df.at[tree, 'error'] = 'Invalide code in ownership'

            else:
                
                df.at[tree, 'error'] = wMessage + '; invalide code in ownership'


        # Record 'invalide species code' in the Error column if species code used is not in the species code column of the speciesTable
        wMessage = df.at[tree, 'error']

        # if df.at[tree, 'species'] not in speciesTable['species'].tolist():
        if pd.isnull(df.at[tree, 'species']):

            if df.at[tree, 'error'] == 'ok':

                df.at[tree, 'error'] = 'Invalide species code'

            else:
                
                df.at[tree, 'error'] = wMessage + '; invalide species code'

        # Record a warning if identified only to genus     
        wMessage = df.at[tree, 'warning']

        if pd.notna(sppName):

            if 'species' in sppName: # Entries identified only to genus will have the word species in the name like Maple Species.  If this happens, record a warning

                if wMessage == 'ok':

                    df.at[tree, 'warning'] = 'Only genus identified'

                else:
                    
                    df.at[tree, 'warning'] = wMessage + '; only genus identified'

        
        # remove rows in the output table (df) that have ok in both the warning and error columns in otherwords there are no problems
        for tree in trees:
            df = df[(df["warning"].str.contains("ok") & df["error"].str.contains("ok")) == False]
            
        dfCheck = df.copy()

        df.drop(['error', 'warning'], axis=1, inplace=True)

        st.markdown('---')
        st.subheader('Errors and Warnings')
        st.markdown('''The following table shows entries with errors and warnings.  Scroll to the right to view the messages in the final two columns. 
                        Warnings highlight issues that may result in some lost information whereas **errors _may_ result in the app crashing.  You should 
                        correct errors before proceeding.**
                        You can filter the columns just as you would in the main table.
        ''')

        # Format the output for the data checking table       
        gb = GridOptionsBuilder.from_dataframe(dfCheck)
        gb.configure_pagination(enabled=True)
        gb.configure_default_column(editable=True, filter=True, fit_columns_on_grid_load = True,)
        gb.configure_column(field='error',editable=False, filter = True, wrapText=True, autoHeight = True)
        gb.configure_column(field='warning',editable=False, filter = True, wrapText=True, autoHeight = True)
            
        gridOptions = gb.build()

        gridReturn = AgGrid(dfCheck,
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
            height = 500, 
            theme = 'fresh',
            enable_enterprise_modules=True, # enables right click and fancy features - can add license key as another parameter (license_key='string') if you have one
            key='check_grid', 
            reload_data=True, # allows modifications to loaded_data to update this same grid entity
            update_mode=GridUpdateMode.NO_UPDATE,
            data_return_mode="FILTERED_AND_SORTED")

        gridReturnData = gridReturn['data']

        #Option to save the data checking table as a spreadsheet
        towrite = io.BytesIO()
        downloaded_file = gridReturn['data'].to_excel(towrite, encoding='utf-8', index=False, header=True, sheet_name = 'summary')
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode()  # some strings
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="NwCheckData.xlsx">Click here to save your data as an Excel file</a>'
        st.markdown(linko, unsafe_allow_html=True)

def setupSidebar(df):
    """
    This def sets up the Streamlit sidebar which calls various functions using the selected dataframe (select_df)
    """ 

    # st.sidebar.warning("If any functions are selected below, please deselect them ALL before proceeding with 'Check Data'")
    # checkDataButton = st.sidebar.button("Check Data")
    
    # if checkDataButton:
    #     checkData(select_df)

    selectFunctionForm = st.sidebar.form(key = 'selectFunction')
    selectFunctionForm.header('Select the function(s) you want to display ')
    selectFunction = selectFunctionForm.multiselect('',['Check Data','Map Trees', 'Pivot Table', 'Tree Diversity', 
                                                    'Species Origin', 'Tree Condition', 'Relative DBH', 
                                                    'Suitability & Invasivity', "Ownership"])
    
    selectFunctionForm.form_submit_button("Continue")

    if 'Check Data' in selectFunction:
        
        # if len(selectFunction) >1:
        #     st.warning("""Before running the "check Data" function please make sure that all other functions are closed.  
        #     Deselect any functions in the sidebar that are currently selected and then presss 'Proceed with Data Checking'.""")
            
        #     proceedButton = st.button('Proceed with Data Checking')

        #     if proceedButton:
        checkData(select_df)
      
    if 'Map Trees' in selectFunction:
        mapItFolium(select_df)

    if 'Pivot Table' in selectFunction:
        pivTable(select_df)
    
    if 'Tree Diversity' in selectFunction:
        diversity(select_df)    

    if 'Species Origin' in selectFunction:
        speciesOrigin(select_df)

    if 'Ownership' in selectFunction:
        ownership(select_df)

    if 'Tree Condition' in selectFunction:
        treeCondition(select_df)
        
    if 'Relative DBH' in selectFunction:
        relativeDBH(select_df)

    if 'Suitability & Invasivity' in selectFunction:
        speciesSuitablity(select_df)


def mapItFolium(mapData):

    '''Generates a folium map using the selected dataframe
    '''
    
    st.markdown("___")
    
    
    pointSizeSlider = st.slider('Move the slider to adjust the point size', min_value = 2, max_value = 20, value =4)
        
    if mapData.empty:
        st.warning("Be sure to finish selecting the filtering values in the sidebar to the left.")

    # Drop entries with no latitude or longitude values entered
    mapData = mapData[mapData['latitude'].notna()] 
    mapData = mapData[mapData['longitude'].notna()]

    mapData['crown_radius'] = mapData['crown_width']/2

    #calculate the average Latitude value and average Longitude value to use to centre the map
    avLat = mapData['latitude'].mean()  
    avLon = mapData['longitude'].mean()
    
    #calculate the avergae lat and lon for centering the map and the max and min values to set the bounds of the map
    avLat=mapData['latitude'].mean()
    avLon=mapData['longitude'].mean()
    maxLat=mapData['latitude'].max()
    minLat=mapData['latitude'].min()
    maxLon=mapData['longitude'].max()
    minLon=mapData['longitude'].min()
    
    #setup the map
    treeMap = folium.Map(location=[avLat, avLon],  
        zoom_start=5,
        max_zoom=100, 
        min_zoom=1, 
        width ='100%', height = '100%', 
        prefer_canvas=True, 
        control_scale=True,
        tiles='OpenStreetMap'
        )

    treeMap.fit_bounds([[minLat,minLon], [maxLat,maxLon]])

    mapData.apply(lambda mapData:folium.CircleMarker(location=[mapData["latitude"], mapData["longitude"]], 
        color='white', # use a white border on the circle marker so it will show up on satellite image
        stroke = True,
        weight = 1,
        fill = True,
        fill_color=mapData['defectColour'],
        fill_opacity = 0.6,
        line_color='#000000',
        radius= pointSizeSlider, #setup a slide so the use can chage the size of the marker
        tooltip = mapData['tree_name'],
        popup = folium.Popup(mapData["description"], 
        name = "Points",
        max_width=450, 
        min_width=300)).add_to(treeMap), 
        axis=1)

    #have an ESRI satellite image as an optional base map
    folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Satellite',
        overlay = False,
        control = True
       ).add_to(treeMap)

    # add a fullscreen option and layer control to the map
    Fullscreen().add_to(treeMap)
    folium.LayerControl().add_to(treeMap)
    
    # Show the map in Streamlit
    folium_static(treeMap)

    #Add the legend saved at github called mapLegend.png
    # st.image(currentDir + 'mapLegend.png')
    
    st.markdown("___")

def pivTable(ptab):
    """Setup a pivot table for more detailed data eexploration"""

    try:
        
        st.markdown("___")
        st.header('Pivot Table Analysis')

        numCols = st.radio('Single or Multiple Columns?', ('Single', 'Multiple'))

        ptForm = st.form(key = 'ptFunction')
        r = ptForm.selectbox('Select the row for your table', options = ptab.columns)
        
        if numCols == 'Multiple':
            c = ptForm.selectbox('Select the column for your table', options = ptab.columns)
        
        v = ptForm.selectbox('Select the value for your table', options = ptab.columns)
        f = ptForm.selectbox('Select the value for your function', options = ['sum', 'mean', 'count' ])
        
        ptForm.markdown('___')

        ptCol1, ptCol2, ptCol3, ptCol4 = ptForm.columns(4)

        showTotal = ptCol1.radio('Show column total?', ('Yes', 'No'))
        decimalNumber = ptCol2.number_input('Enter the number of decimal places for all values in table.', value  = 1)

        if f != 'mean':

            if showTotal =='Yes':
                selectMargins=True
                selectMargins_name = 'Total'
            else:
                selectMargins=False
                selectMargins_name = 'Total'

        else:

            selectMargins=False
            selectMargins_name = ''

        if f == 'count':
            f = pd.Series.nunique
            funcType = 'count'

        else: funcType = f

        ptSubmitButton = ptForm.form_submit_button("Show Pivot Table")

        if ptSubmitButton:
            
            if numCols=='Multiple':

                ptable = pd.pivot_table(ptab, 
                    index = r, 
                    columns = c, 
                    values = v, 
                    aggfunc = f,
                    margins=selectMargins,
                    margins_name=selectMargins_name)

                st.subheader(f'The {(funcType)} of {v} by {r} and {c}.')

            else:

                ptable = pd.pivot_table(ptab, 
                    index = r, 
                    values = v, 
                    aggfunc = f,
                    margins=selectMargins,
                    margins_name=selectMargins_name)

                st.subheader(f'The {(funcType)} of {v} by {r}.')

            ptable.reset_index(inplace=True)
            ptable = ptable.round(decimals = decimalNumber)

            # Aggrid Table setup for pivot table
            gb = GridOptionsBuilder.from_dataframe(ptable)
            gb.configure_pagination(enabled=True)
            gb.configure_default_column(editable=False, filter=True, width = 50, type = 'numericColumn')

            gridOptions = gb.build()

            pivotReturn = AgGrid(ptable,
                fit_columns_on_grid_load=True,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                height = 500, 
                theme = 'streamlit',
                enable_enterprise_modules=True, # enables right click and fancy features - can add license key as another parameter (license_key='string') if you have one
                key='pivotGrid', # stops grid from re-initialising every time the script is run
                reload_data=True, # allows modifications to loaded_data to update this same grid entity
                # update_mode=GridUpdateMode.FILTERING_CHANGED,
                update_mode=GridUpdateMode.NO_UPDATE,
                data_return_mode="FILTERED_AND_SORTED")

            privotReturnData = pivotReturn['data']

            #Option to save pivot table as a spreadsheet
            towrite = io.BytesIO()
            downloaded_file = pivotReturn['data'].to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="NwAnalyticsPivot.xlsx">Click here to save your data as an Excel file</a>'
            st.markdown(linko, unsafe_allow_html=True) 
                
    except:
        st.error("Oh no!  Something went wrong.  Check to make sure that your filters in the pivot tabel setup make sense.")
   
def diversity(data):
    """Analyze tree diversity"""

    # st.write(data.columns)

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

    speciesPie = px.pie(topTenPlusOther, 
        values='frequency', 
        names = divLevel,
        color = divLevel,
        color_discrete_map = colorsDict
        )

    speciesPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    speciesPie.update_layout(showlegend=False)
    speciesPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    

    with st.expander("Click to view tabular data.", expanded=False):
        divTable = ff.create_table(topTenPlusOther.round(decimals = 0))
        st.plotly_chart(divTable)

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
    
    CpaPie = px.pie(topTenCpaPlusOther, 
        values='Crown Projection Area', 
        names = divLevel,
        color = divLevel,
        color_discrete_map = colorsDict
        )

    CpaPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    CpaPie.update_layout(showlegend=False)
    CpaPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(CpaPie)
    
def speciesOrigin(data):
    """Analyze speecies origin i.e.native vs non-native"""
        
    data = data.loc[data['diversity_level'] != 'other']

    avLat = data['latitude'].mean()  
    avLon = data['longitude'].mean()

    st.markdown("___")
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


    # @st.cache_data(show_spinner=True)
    # def get_ecodistricts():

    #     ''' Determines the Ecodistrict that the point with the avergage Latitude and longitude is in. An option to show a map with the Ecodistrict and  point 
    #     is also provided.  The Ecodistrict map is read a a geopackage called OntarioEcodistricts from my github repo.  This is all done within a Streamlit expander
    #     so the user can swith it on and off.
    #     '''
        
    #     ecod = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioEcodistricts.gpkg")
    #     ecod.drop(['GEOMETRY_U', 'EFFECTIVE_', 'SYSTEM_DAT', 'OGF_ID', 
    #                 'SHAPE.AREA', 'SHAPE.LEN', 'OBJECTID'], axis=1, inplace=True)

    #     ecod.rename(columns={'ECODISTR_1': 'ecodistrict', 
    #         'ECODISTRIC':'ecodistrict_name', 'ECOREGION_':'ecoregion_name',
    #         'ECOREGIO_1':'ecoregion', 'ECOZONE_NA':'ecozone_name'}, inplace = True)
            
    #     ecod = ecod.to_crs('EPSG:4326')

    #     return ecod

    # ecod = get_ecodistricts()

    # pointDf = pd.DataFrame(
    #     {'Name': 'Average Point',
    #     'latitude': avLat,
    #     'longitude': avLon
    #     }, index=[0])

    # pointgdf = gpd.GeoDataFrame(pointDf, crs="EPSG:4326",
    #                             geometry=gpd.points_from_xy(pointDf.longitude, pointDf.latitude))
    
    # # pointgdf.to_crs('EPSG 4326')

    # pip = gpd.tools.sjoin(pointgdf, ecod, predicate="within", how='left')

    # ecodName = (pip.ecodistrict[0])

    # st.write("Your data is in Ecodistrict: ", ecodName)

    # with st.expander("Click here to see a map of the Ecodistrict.         Click here again to close the map...", expanded=False):

    #     with st.spinner("Please wait while your map is set up."):

    #         ecodMap = ecod.explore()

    #         folium.CircleMarker(location=[avLat, avLon],
    #                     zoom_start = 15, 
    #                     color='white', # use a white border on the circle marker so it will show up on satellite image
    #                     stroke = True,
    #                     weight = 2,
    #                     fill = True,
    #                     fill_color='red',
    #                     fill_opacity = 0.2,
    #                     line_color='#000000',
    #                     tooltip = ecod['ecodistrict'],
    #                     ).add_to(ecodMap)

    #         folium_static(ecodMap)
    
    # By frequency

    st.subheader("Origin by the number of trees (frequency)")

    originData = data.loc[: , ['seRegion', 'tree_name']]

    originData.fillna('not assessed')

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


def ownership(data):
    """Analyze tree ownership - City, Provate or Jointly owned"""

    data = data.loc[data['diversity_level'] != 'other']

    ownershipText = {'c':'City', 'p':'Private', 'j':'Joint'}
    data['ownership_code'] = data['ownership_code'].map(ownershipText)

    st.markdown("___")
    st.header('Tree Ownership Summary')
    
    with st.expander("Click here to read an explanation of Ownership summary.", expanded=False):
        
            st.markdown('''Coming soon ..... 
                '''
            )
    
        # By frequency

    st.subheader("Ownership by the number of trees (frequency)")

    ownershipData = data.loc[: , ['ownership_code', 'tree_name']]

    ownershipData.fillna('not assessed')

    ownershipPT = pd.pivot_table(ownershipData, index='ownership_code', aggfunc='count')
    ownershipPT.reset_index(inplace=True)
    
    ownershipPT.rename(columns = {'tree_name': 'frequency'},inplace = True)


    ownershipPie = px.pie(ownershipPT, values='frequency', names = 'ownership_code')
    
    ownershipPie.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    ownershipPie.update_layout(showlegend=False)
    ownershipPie.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(ownershipPie)

    # By CPA

    st.subheader("Ownership by crown projection area (cpa)")

    ownershipDataCPA = data.loc[: , ['ownership_code', 'cpa']]

    ownershipPTCPA = pd.pivot_table(ownershipDataCPA, index='ownership_code', aggfunc='sum')
       
    ownershipPTCPA.reset_index(inplace=True)
    
    # ownershipPTCPA.rename(columns = {'ownership' : 'Ownership'},inplace = True)
    
    ownershipPieCPA = px.pie(ownershipPTCPA, values='cpa', names = 'ownership_code')
    
    ownershipPieCPA.update_traces(insidetextorientation='radial', textinfo='label+percent') 
    ownershipPieCPA.update_layout(showlegend=False)
    ownershipPieCPA.update_traces(textfont_size=15,
                  marker=dict(line=dict(color='#000000', width=1)))
    
    st.plotly_chart(ownershipPieCPA)


def treeCondition(data):
    """Summarize tree condition """

    st.markdown("___")
    st.header('Tree Condition Summary')
    
    try:
    
        cols = ['0', '1', '2', '3']

        df = pd.DataFrame(index = condColumns, columns = cols)

        for cond in condColumns:
            
            myValues = pd.to_numeric(data[cond], errors = 'coerce').value_counts(bins = 4)
            
            df.at[cond,'0'] = myValues.iloc[0]
            df.at[cond,'1'] = myValues.iloc[1]
            df.at[cond,'2'] = myValues.iloc[2]
            df.at[cond,'3'] = myValues.iloc[3]

        df.reset_index(inplace=True)
        df = df.rename(columns = {'index':'Condition Attribute'})
        
        with st.expander("Click here to show Data Summary by Condition Attribute and Score", expanded=False):

            condTable = ff.create_table(df)
            st.plotly_chart(condTable)


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
        
        conditionPieCPA = px.pie(conditionPTCPA, values='cpa', names = 'defects')
        
        conditionPieCPA.update_traces(insidetextorientation='radial', textinfo='label+percent') 
        conditionPieCPA.update_layout(showlegend=False)
        conditionPieCPA.update_traces(textfont_size=15,
                    marker=dict(line=dict(color='#000000', width=1)))
        

        st.subheader("Condition by Crown Projection Area (cpa)")
        st.plotly_chart(conditionPieCPA)

    except ValueError:

        st.warning('''Oh oh!  There may be a problem with your data.  Run the "Check Data" function (in the sidebar) 
        and look for errors in the column at the right of the table that is generated.  You can filter the error column
        in the table just as you would in the main table to find everything that isn't "ok".  Correct any errors in your data input file
        then re-start this app, re-load the corrected file and proceed. Only 0, 1, 2 or 3 (0 or 1 for conks) are valid entries in any of the 
        condition columns (reduced_crown to recent_trenching). Any other value, including a blank, in these columns will 
        cause NWAnalytics3 to stop working!''')
        

def relativeDBH(data):
    
    """Summarize Relative DBH"""

    st.markdown("___")

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
    
    numberNan = data['dbh_class'].isnull().sum()
    
    if numberNan != 0:
        if numberNan == 1:
            st.write('There is 1 entry with no DBH Class recorded.  This will be omitted from this anlysis.')    
        else:
            st.write('There are ' + str(numberNan) + ' entries with no DBH Class recorded.  These will be omitted from this anlysis.')

    data = data.loc[data['diversity_level'] == 'species']

    data.dropna(subset=['dbh'], inplace = True)
    data.dropna(subset=['dbh_class'], inplace = True)
    data.dropna(subset=['rdbh_class'], inplace = True)
   
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

    with st.expander("Click here to show DBH class by Frequency and Target ", expanded=False):
        

        rdbhTable = ff.create_table(dbhPT.round(decimals = 0))
        
        st.plotly_chart(rdbhTable)
    
    st.plotly_chart(dbhFig)

    realtiveDbhData = data.loc[: , ['rdbh_class', 'tree_name']]
    
    relativeDbhPT = pd.pivot_table(realtiveDbhData, index='rdbh_class', aggfunc='count')
    relativeDbhPT.reset_index(inplace=True)
    relativeDbhPT.rename(columns = {'rdbh_class': 'Relative DBH Class', 'tree_name': 'Frequency'},inplace = True)

    relativeDbhPT = relativeDbhPT.head(4)

    numberOfEntries = relativeDbhPT['Frequency'].sum()

    relativeDbhPT["Target"] = [numberOfEntries*0.4, numberOfEntries*0.3, numberOfEntries*0.2, numberOfEntries*0.1]

    rdbhFig = go.Figure(data=[
        go.Bar(name='Current', x= relativeDbhPT['Relative DBH Class'], y=relativeDbhPT['Frequency']),
        go.Bar(name='Target', x=relativeDbhPT['Relative DBH Class'], y=relativeDbhPT['Target'])])

    rdbhFig.update_layout(barmode='group', xaxis=dict(title_text='Relative DBH CLass'), yaxis = dict(title_text='Frequency'))
    
    st.header("Relative DBH Class Frequency")

    st.plotly_chart(rdbhFig)


def speciesSuitablity(data):
    """Summarize species suitability"""

    st.markdown("___")
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
    
    with st.expander("Click to view tabular data.", expanded=False):
        suitabilityTable = ff.create_table(suitabilityPT.round(decimals = 0))
        st.plotly_chart(suitabilityTable)
        
    st.plotly_chart(suitabilityPie)


    st.subheader('Suitability by crown projection area (cpa)')

    suitabilityDataCPA = data.loc[: , ['suitability', 'cpa']]
    suitabilityPTCPA = pd.pivot_table(suitabilityDataCPA, index='suitability', aggfunc='sum')
    suitabilityPTCPA.reset_index(inplace=True)
    
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

    st.markdown("___")
    st.header('Tree Species Invasivity Summary (Ontario)')
    
    with st.expander("Click here to read about species invasivity", expanded=False):
        st.markdown('''The tree species indicated as invasive are based on data shown in https://www.ontarioinvasiveplants.ca/invasive-plants/species/''')

    st.subheader('Invasivity by the number of trees (frequency)')

    invasivityData = data.loc[: , ['species', 'invasivity', 'tree_name']]

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
    
    with st.expander("Click to view invasive vs. non-invasive summary data.", expanded=False):

        invasivityTable = invasivityPT.drop('species', axis=1, inplace=True)

        invasivityTable = ff.create_table(invasivityPT.round(decimals = 0))
        st.plotly_chart(invasivityTable)

    # invasiveSpecies = data.loc[data['invasivity'] == 'invasive', 'species']
    
    with st.expander("Click to view a list of invasive tree species in your data set.", expanded=False):
   
        invasiveSpeciesOnly = invasivityData.loc[invasivityData['invasivity']=='invasive']     
        invasiveSpeciesOnly.rename(columns = {'tree_name': 'frequency'},inplace = True)
        invasivitySpeciesTable = pd.pivot_table(invasiveSpeciesOnly, index='species', values = 'frequency', aggfunc='count')
        invasivitySpeciesTable.reset_index(inplace=True)
        invasivitySpeciesTable = ff.create_table(invasivitySpeciesTable)
        st.plotly_chart(invasivitySpeciesTable)
    
    
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
    
    # with st.expander("Click to view tabular data.", expanded=False):
    #     invasivityCPATable = ff.create_table(invasivityPTCPA.round(decimals = 0))
    #     st.plotly_chart(invasivityCPATable)

    st.plotly_chart(invasivityPieCPA)

# Once a file name is selected, setup the sidebar.  From within the sidebar the user 
# will select functions which will run the rest of the program.  In other words, running setupSidebar
# launches the whole program.

if fileName is not None:
    setupSidebar(df)

    



# %%
