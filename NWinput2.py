import pandas as pd
import geopandas as gpd
import streamlit as st
import io
import base64
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode
from io import BytesIO
import xlsxwriter

st.title('Neighbourwoods Data Entry and Clean-up')

st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

currentDir = "https://raw.githubusercontent.com/WAKenney/NWAnalytics/main/"

speciesFile = currentDir + 'NWspecies220522.xlsx'

@st.cache_data(show_spinner="Loading the species table, please wait ...")
def getSpeciesTable(): 
    speciesTable = pd.read_excel(speciesFile,sheet_name = "species")
    return speciesTable

speciesTable = getSpeciesTable()

activeEcodist = '6E-16'

attributeNames = ['reduced_crown', 'unbalanced_crown', 'defoliation',
    'weak_or_yellow_foliage', 'dead_or_broken_branch',  'lean', 'poor_branch_attachment',	
    'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity', 
    'trunk_rot_or_cavity', 'confined_space', 'crack', 'exposed_roots', 'girdling_roots', 'recent_trenching']

fileName ='empty'

fileName = st.file_uploader("Browse for or drag and drop the name of your Neighburwoods MS excel workbook", 
    type = ['xlsm', 'xlsx', 'csv'], 
    key ='fileNameKey')

@st.cache_data(show_spinner="Loading your data, please wait ...")
def getData(fileName):

    if fileName is not None:

        df_trees = pd.DataFrame()
        df_streets = pd.DataFrame()

        try:
        
            df_trees = pd.read_excel(fileName, sheet_name = 'trees', header = 0)

            # df_trees = df_trees.rename(columns = {'Block ID':'Block Id','Hard Surface':'Hard surface','house_number':'House Number',
            #                                         'Ht to Crown Base':'Ht to base','Latitude':'Y coordinate','Location Code':'location_code',
            #                                         'Longitude':'X coordinate','Ownership Code':'ownership_code','Tree Name':'Tree name',
            #                                         'tree_number':'Tree No','Weak or Yellowing Foliage':'Weak or Yellow Foliage'})
            
        except:
            st.error("Ooops something is wrong with your data file!")

        df_streets = pd.read_excel(fileName, sheet_name = 'streets', header = 0)
        if df_streets.iat[0,0] == 'street_code':
            df_streets = pd.read_excel(fileName, sheet_name = 'streets', header = 1)
        if df_streets.iat[0,0] == 'street':
            df_streets = pd.read_excel(fileName, sheet_name = 'streets', header = 1)
       
        dataCols =df_trees.columns
        
        df_streets=df_streets.rename(columns = {'ADDRESS':'street_code','ADDRESSNAME':'street_name','street':'street_code','street name':'street_name' })

        # df_streets['street_code'] = df_streets['street_code'].str.lower()

        # if 'Block Id' in dataCols:
        #     df_trees=df_trees.rename(columns = {'Block ID':'block'})
        
        # if "Ownership code" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Ownership code':'ownership_code'})

        # if "Crown Width (m)" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Crown Width (m)':'Crown Width'})

        # if "Date(dd/mm/yy)" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Date(dd/mm/yy)':'Date'})

        # if "DBH (cm)" in dataCols:
        #     df_trees=df_trees.rename(columns = {'DBH (cm)':'DBH'})

        # if "% Hard surface" in dataCols:
        #     df_trees=df_trees.rename(columns = {'% Hard surface':'Hard surface'})

        # if "Ht to base of crown." in dataCols:
        #     df_trees=df_trees.rename(columns = {'Ht to base of crown.':'Ht to base'})

        # if "Location Code" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Location Code':'location_code'})

        # if "location" in dataCols:
        #     df_trees=df_trees.rename(columns = {'location':'location_code'})

        # if "No. of Stems" in dataCols:
        #     df_trees=df_trees.rename(columns = {'No. of Stems':'Number of Stems'})

        # if "Ownership Code" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Ownership Code':'ownership_code'})

        # if "ownership" in dataCols:
        #     df_trees=df_trees.rename(columns = {'ownership':'ownership_code'})

        # if "Species Code" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Species Code':'species_code'})

        # if "Street Code" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Street Code':'street_code'})

        # if "Total Height (m)" in dataCols:
        #     df_trees=df_trees.rename(columns = {'Total Height (m)':'Total Height'})

        if 'xy' in dataCols:
            df_trees[['Latitude', 'Longitude']] = df_trees['xy'].str.split(',', 1, expand=True)
            df_trees.drop('xy', axis=1, inplace=True)

        #check to make sure Lat and Lon aren't mixed up.  If average Latitude is greater than 60 it is LIKELY really longitude so swap the names

        # if avLat > 60:   
        #     df_trees=df_trees.rename(columns = {'Y coordinate':'Latitude','X coordinate':'Longitude'})

        df_trees=df_trees.rename(columns = {'Tree name':'tree_name','Date':'date','Block Id':'block','Block ID':'block','Tree No':'tree_number',
                                'House Number':'house_number',
                                'location':'location_code','Location Code':'location_code',
                                'ownership':'ownership_code','Ownership code':'ownership_code',
                                'Crown Width':'crown_width','Number of Stems':'number_of_stems','DBH':'dbh',
                                'Hard surface':'hard_surface','Hard Surface':'hard_surface','Ht to base':'height_to_crown_base',
                                'Total Height':'total_height','Reduced Crown':'reduced_crown','Unbalanced Crown':'unbalanced_crown',
                                'Defoliation':'defoliation','Weak or Yellow Foliage':'weak_or_yellow_foliage','Weak or Yellowing Foliage':'weak_or_yellow_foliage',
                                'Dead or Broken Branch':'dead_or_broken_branch','Lean':'lean','Poor Branch Attachment':'poor_branch_attachment',
                                'Branch Scars':'branch_scars','Trunk Scars':'trunk_scars','Conks':'conks','Rot or Cavity - Branch':'branch_rot_or_cavity',
                                'Rot or Cavity - Trunk':'trunk_rot_or_cavity','Confined Space':'confined_space',
                                'Crack':'crack','Girdling Roots':'girdling_roots', 'Exposed Roots': 'exposed_roots', 'Recent Trenching':'recent_trenching',
                                'Cable or Brace':'cable_or_brace','Conflict with Wires':'wire_conflict',
                                'Conflict with Sidewalk':'sidewalk_conflict','Conflict with Structure':'structure_conflict',
                                'Conflict with another tree':'tree_conflict','Conflict with Traffic Sign':'sign_conflict'})
        
        df_trees['species_code'] = df_trees['species_code'].str.lower()
        df_trees['species_code'] = df_trees['species_code'].str.strip()

        df_trees['street_code'] = df_trees['street_code'].str.lower()
        df_trees['street_code'] = df_trees['street_code'].str.strip()

        df_trees['ownership_code'] = df_trees['ownership_code'].str.lower()
        df_trees['ownership_code'] = df_trees['ownership_code'].str.strip()

        df_trees['location_code'] = df_trees['location_code'].str.lower()
        df_trees['location_code'] = df_trees['location_code'].str.strip()
        
        
        if 'tree_name' not in dataCols:
            df_trees["tree_name"] = df_trees.apply(lambda x : str(x["block"]) + '-' +  str(x["tree_number"]), axis=1)
       
        df_trees = df_trees.merge(df_streets, on="street_code", how = "left")

    return df_trees

df_trees = getData(fileName)

def fixTitles():

    #  Column titles from the Neighourwoods MS 2.6 workbook
    nwWkbkTitles = ['tree index','Tree name', 'Date', 'Block Id', 'Tree No', 'House Number', 'street_code', 'species_code', 'location_code', 
    'ownership_code', 'Number of Stems', 'DBH', 'Hard surface', 'Crown Width', 'Ht to base', 'Total Height', 'Reduced Crown', 
    'Unbalanced Crown', 'Defoliation', 'Weak or Yellow Foliage', 'Dead or Broken Branch', 'Lean', 'Poor Branch Attachment', 
    'Branch Scars', 'Trunk Scars', 'Conks', 'Rot or Cavity - Branch', 'Rot or Cavity - Trunk', 'Confined Space', 'Crack', 
    'Girdling Roots', 'Exposed Roots', 'Recent Trenching', 'Cable or Brace', 'Conflict with Wires', 'Conflict with Sidewalk', 
    'Conflict with Structure', 'Conflict with another tree', 'Conflict with Traffic Sign', 'Comments', 'X coordinate', 'Y coordinate']

    #  Column titles from the Neighourwoods Memento data entry library
    mementoTitles = ['Tree name', 'Date', 'Block Id', 'Tree No', 'House Number', 'street_code', 'species_code', 'location', 
    'ownership', 'Number of Stems', 'DBH', 'Hard surface', 'Crown Width', 'Ht to base', 'Total Height', 'Reduced Crown', 
    'Unbalanced Crown', 'Defoliation', 'Weak or Yellow Foliage', 'Dead or Broken Branch', 'Lean', 'Poor Branch Attachment', 
    'Branch Scars', 'Trunk Scars', 'Conks', 'Rot or Cavity - Branch', 'Rot or Cavity - Trunk', 'Confined Space', 'Crack', 
    'Girdling Roots', '', 'Recent Trenching', 'Cable or Brace', 'Conflict with Wires', 'Conflict with Sidewalk', 
    'Conflict with Structure', 'Conflict with another tree', 'Conflict with Traffic Sign', 'Comments', 'xy', 'Photo 1', 'Photo 2']

    #  Column titles from the Neighbourwoods_Data_ENTRY_141221.xlsm workbook
    nwInputTitles = ['Date(dd/mm/yy)', 'Block', 'Tree No', 'House Number', 'Street Code', 'Species Code', 'Location Code', 
    'Ownership Code', 'No. of Stems', 'DBH (cm)', '% Hard surface', 'Crown Width (m)', 'Ht to base of crown.', 'Total Height (m)', 'Reduced Crown', 
    'Unbalanced Crown', 'Defoliation', 'Weak or Yellow Foliage', 'Dead or Broken Branch', 'Lean', 'Poor Branch Attachment', 
    'Branch Scars', 'Trunk Scars', 'Conks', 'Rot or Cavity - Branch', 'Rot or Cavity - Trunk', 'Confined Space', 'Crack', 
    'Girdling Roots', 'Recent Trenching', 'Exposed Roots', 'Cable or Brace', 'Conflict with Wires', 'Conflict with Sidewalk', 
    'Conflict with Structure', 'Conflict with another tree', 'Conflict with Traffic Sign', 'Comments', 'X coordinate', 'Y coordinate']

    dfTitles = df_trees.columns

    for nwWkbkTitle in nwWkbkTitles:
        if nwWkbkTitle not in dfTitles:
            st.warning("Ooops ", nwWkbkTitle, " isn't a column in your dataset!")

        if inputType == 'Neighourwoods Memento data entry library':
            st.info ('You have selected "Neighourwoods Memento data entry library" as your input data type')
    else:
        st.info ('You have selected "Neighbourwoods_Data_ENTRY.xlsm workbook" as your input data type')    

if 'exposed_roots' not in df_trees.columns:
    df_trees.insert(30,"exposed_roots",'')

cols = df_trees.columns


def aggFilter(df):
    '''
    Sets up the data in a table for viewing and filtering
    
    '''

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_default_column(editable=True, filter=True)
    gb.configure_column(field='Description', header_name='Tree Description',
        editable=False, filter = False, wrapText=True, autoHeight = True)
    # gb.configure_side_bar(filters_panel=True, columns_panel=False, defaultToolPanel='')

    gridOptions = gb.build()

    gridReturn = AgGrid(df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        height = 500, 
        theme = 'blue',
        enable_enterprise_modules=True, # enables right click and fancy features - can add license key as another parameter (license_key='string') if you have one
        key='inputGrid', # stops grid from re-initialising every time the script is run
        reload_data=True, # allows modifications to loaded_data to update this same grid entity
        update_mode=GridUpdateMode.MANUAL,
        data_return_mode="FILTERED_AND_SORTED")

    gridReturnData = gridReturn['data']

    towrite = io.BytesIO()
    downloaded_file = gridReturn['data'].to_excel(towrite, encoding='utf-8', index=False, header=True, sheet_name = 'summary')
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()  # some strings
    linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="NWinputData.xlsx">Click here to save your data as an Excel file</a>'
    st.markdown(linko, unsafe_allow_html=True)

    originalSize = len(df.index)
    filteredSize = len(gridReturn['data'].index)
            
    if filteredSize<originalSize:
        st.markdown(f"__NOTE__: You are using filtered data with {filteredSize} entries selected.  All functions will now operate on this filtered data. Be sure to remove ALL filters when you want to use the full (unfiltered) dataset.")

    return gridReturnData

# def getSpeciesTable(): 
#     speciesTable = pd.read_excel(speciesFile,sheet_name = "species")
#     return speciesTable

# speciesTable = getSpeciesTable()

def getOrigin():
    origin = pd.read_excel(speciesFile, sheet_name = 'origin')

    return origin

df_origin = getOrigin()

def getEcodistricts():
    gpd_ecodistricts = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioEcodistricts.gpkg")
    return gpd_ecodistricts

gpd_ecodistricts = getEcodistricts()

def getCodes():
    codes = pd.read_excel(speciesFile, sheet_name = 'codes')
    
    return codes

df_codes = getCodes()

df_trees = df_trees.merge(speciesTable.loc[:,['species_code','family', 'genus','species', 'Max DBH', 'invasivity',
    'suitability', 'diversity_level']], how='left')

df_trees=df_trees.rename(columns = {'Max DBH':'max_dbh'})

def origin(df_trees):
    df_trees = df_trees.merge(df_origin.loc[:,['species_code', activeEcodist]], how='left')
    df_trees=df_trees.rename(columns = {activeEcodist:'origin'})

    return df_trees

df_trees = origin(df_trees)

def cpa(cw):
    '''
    calculate crown projection area
    '''
    if pd.isnull(df_trees['crown_width'].iloc[0]):
        cpa = 'n/a'
    
    else:
       cpa = ((cw/2)**2)*3.14

    # cpa= int(cpa)
    
    return cpa

df_trees['Crown Projection Area (CPA)'] = df_trees['crown_width'].apply(lambda x: (cpa(x)))

df_trees["Address"] = df_trees.apply(lambda x : str(x["house_number"]) + ' ' +  str(x["street_name"]), axis=1)

def dbhClass(df):
    if df['dbh']<20:
        return 'I'
    elif df['dbh']<40:
        return 'II'
    elif df['dbh']<60:
        return 'III'
    else: 
        return 'IV'

df_trees['DBH Class'] = df_trees.apply(dbhClass, axis =1)

def rdbh():
    df_trees['Relative Dbh'] =df_trees.apply(lambda x: 'n/a' if pd.isnull('dbh') else x.dbh/x.max_dbh, axis =1).round(2)

    df_trees.drop('max_dbh', axis=1, inplace=True)

rdbh()

df_trees['Relative DBH Class'] = pd.cut(x=df_trees['Relative Dbh'], bins=[0, 0.25, 0.5, 0.75, 3.0], labels = ['I', 'II', 'III','IV'])


def structural(df):
    if df['unbalanced_crown'] ==3:
        return 'yes' 
    elif df['dead_or_broken_branch'] == 3:
        return 'yes'
    elif df['lean'] == 3:
        return 'yes'
    elif df['dead_or_broken_branch'] == 3:
        return 'yes'
    elif df['poor_branch_attachment'] == 3:
        return 'yes'
    elif df['trunk_rot_or_cavity'] == 3:
        return 'yes'
    elif df['branch_rot_or_cavity'] == 3:
        return 'yes'
    elif df['crack'] == 3:
        return 'yes'
    elif df['cable_or_brace'] == 'y':
        return 'yes'
    else:
        return 'no'

df_trees['Structural Defect']= df_trees.apply(structural, axis =1)

def health(df):
    if df['defoliation'] ==3:
        return 'yes' 
    elif df['weak_or_yellow_foliage'] == 3:
        return 'yes'
    elif df['trunk_scars'] == 3:
        return 'yes'
    elif df['conks'] == 3:
        return 'yes'
    elif df['girdling_roots'] == 3:
        return 'yes'
    elif df['recent_trenching'] == 3:
        return 'yes'
    else:
        return 'no'

df_trees['Health Defect']= df_trees.apply(health, axis =1)

def desc(df):

    df_cond = pd.DataFrame(columns=attributeNames)

    df['Description'] = []

    df['Description'] = "Tree {} is a {} at {}. The most recent assessment was done on {}.".format(df['tree_name'], df['species'], df['Address'], df['date'])
    # df['Description'] = f"Tree {df['tree_name']} is a {df['species']} at {df['Address']}. The most recent assessment was done on {df['date']:%B %d, %y}."

    if df['Structural Defect'] == 'yes' and df['Health Defect'] =='yes':
        df['Description'] = df['Description'] + ' It has significant structural AND health defects'
    
    elif df['Structural Defect'] == 'yes':
        df['Description'] = df['Description'] + ' It has at least one significant structural defect.'
    
    elif df['Health Defect'] == 'yes':
        df['Description'] = df['Description'] + ' It has at least one significant health defect.'
    
    elif df['Structural Defect'] == 'yes' and df['Health Defect'] =='yes':
        df['Description'] = df['Description'] + ' It has significant structural AND health defects'
    
    else:
        df['Description'] = df['Description'] + ' It has no SIGNIFICANT health or structural defects.'

    df['Description'] = df['Description'] + " It has a DBH of {} cm, a total height of {:,.0f} m and a crown width of {:,.0f}m.".format(df['dbh'], df['total_height'], df['crown_width'])

    if pd.notnull(df['hard_surface']):
        df['Description'] = df['Description'] + " The area under the crown is {:,.0f}% hard surface. ".format(df['hard_surface'])

    return df

df_trees = df_trees.apply(desc, axis =1)

def condition():
    '''This creates a series called code_names holding the column 
    names from df_codes and an empty df called df_cond 
    which is then filled with the text from df_codes 
    corresponding to each of the scores from df_trees for each column 
    in code_names. The result is additon of condition descriptions to
    df_trees['Description']'''

    df_cond = pd.DataFrame(columns=attributeNames)
    
    for column in attributeNames:
        df_cond[column]=df_trees[column].map(df_codes[column]).fillna('')
        
    condition = df_cond.apply(lambda row: ''.join(map(str, row)), axis=1)

    df_trees['Description'] = df_trees['Description'] + condition

condition() # This calls the function condition()

df_trees=df_trees.rename(columns = {'tree_name':'Tree Name', 'date': 'Date', 'block':'Block ID',
    'Tree No':'Tree Number','street_name':'Street','location_code': 'Location Code','ownership_code': 'Ownership Code',
    'crown_width': 'Crown Width','number_of_stems':'Number of Stems','dbh':'DBH',
    'hard_surface':'Hard Surface','height_to_crown_base': 'Ht to Crown Base', 'total_height':'Total Height',
    'reduced_crown':'Reduced Crown','unbalanced_crown':'Unbalanced Crown',
    'defoliation':'Defoliation','weak_or_yellow_foliage':'Weak or Yellowing Foliage','dead_or_broken_branch':'Dead or Broken Branch',
    'lean':'Lean','poor_branch_attachment':'Poor Branch Attachment','branch_scars':'Branch Scars','trunk_scars':'Trunk Scars',
    'conks':'Conks','branch_rot_or_cavity':'Rot or Cavity - Branch','trunk_rot_or_cavity':'Rot or Cavity - Trunk',
    'confined_space':'Confined Space','crack':'Crack','girdling_roots':'Girdling Roots', 'exposed_roots':'Exposed Roots',
    'recent_trenching':'Recent Trenching','cable_or_brace':'Cable or Brace','wire_conflict':'Conflict with Wires',
    'sidewalk_conflict':'Conflict with Sidewalk','structure_conflict':'Conflict with Structure',
    'tree_conflict':'Conflict with Another Tree','sign_conflict':'Conflict with Traffic Sign', 'family':'Family',
    'genus':'Genus', 'species':'Species', 'Relative Dbh': 'Relative DBH', 'origin':'Native', 'suitability':'Species Suitability',
    'diversity_level':'Diversity Level','invasivity':'Invasivity','X coordinate':'Longitude', 'Y coordinate':'Latitude'
    })  

aggFilter(df_trees)

# saveMSbutton = st.button('Click here to save data for use with MS 2.6')

# if saveMSbutton:
#     df_trees.drop(['tree index', 'BLOCK', 'Diversity Level', 'house_number', 'ID', 'Invasivity', 'species_code',
#                    'street_code', 'y'], axis=1, inplace = True)
#     df_trees.rename(columns = {'tree_number':'Tree Number'}, inplace = True)

#     df_trees['Simple Rating'] = "Good"
#     df_trees['Total Demerits'] = 0

#     towrite = io.BytesIO()
#     downloaded_file = df_trees.to_excel(towrite, encoding='utf-8', index=False, header=True)
#     towrite.seek(0)  # reset pointer
#     b64 = base64.b64encode(towrite.read()).decode()  # some strings
#     linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="ForMS2.6.xlsx">Click here to save your data as an Excel file</a>'
#     st.markdown(linko, unsafe_allow_html=True) 
