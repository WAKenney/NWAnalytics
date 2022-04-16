import pandas as pd
import geopandas as gpd
import streamlit as st
import io
import base64
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode

st.title('Neighbourwoods Data Entry and Clean-up')

activeEcodist = '6E-16'

attributeNames = ['reduced_crown', 'unbalanced_crown', 'defoliation',
    'weak_or_yellow_foliage', 'dead_or_broken_branch',  'lean', 'poor_branch_attachment',	
    'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity', 
    'trunk_rot_or_cavity', 'confined_space', 'crack', 'exposed_roots', 'girdling_roots', 'recent_trenching']


attributeNames = ['reduced_crown', 'unbalanced_crown', 'defoliation', 'weak_or_yellow_foliage', 'dead_or_broken_branch',  'lean', 'poor_branch_attachment',	
    'branch_scars', 'trunk_scars', 'conks', 'branch_rot_or_cavity', 'trunk_rot_or_cavity', 'confined_space', 'crack', 'exposed_roots', 'girdling_roots', 'recent_trenching']

df_trees = pd.read_excel(r"C:\Users\HP\Documents\Data\Files\Neighbourwoods\Master files\NWAalytics3\DataEntry\memInput100.xlsx")
   
df_trees.drop(['Species & Location', 'Tree Size', 'Tree Condition', 'Conflicts', 'Comments (optional)', 'X,Y Coordinates',
                'Photos (optional)','Photo 1','Photo 2' ], axis=1, inplace=True)

df_trees=df_trees.rename(columns = {'Tree name':'tree_name','Date':'date','Block Id':'block','Tree Number':'tree_number',
                                    'street_code':'street','House Number':'house_number','location':'location_code','ownership':'ownership_code',
                                    'Crown Width':'crown_width','Number of Stems':'number_of_stems','DBH':'dbh',
                                    'Hard surface':'hard_surface','Ht to base':'height_to_crown_base',
                                    'Total Height':'total_height','Reduced Crown':'reduced_crown','Unbalanced Crown':'unbalanced_crown',
                                    'Defoliation':'defoliation','Weak or Yellow Foliage':'weak_or_yellow_foliage',
                                    'Dead or Broken Branch':'dead_or_broken_branch','Lean':'lean','Poor Branch Attachment':'poor_branch_attachment',
                                    'Branch Scars':'branch_scars','Trunk Scars':'trunk_scars','Conks':'conks','Rot or Cavity - Branch':'branch_rot_or_cavity',
                                    'Rot or Cavity - Trunk':'trunk_rot_or_cavity','Confined Space':'confined_space',
                                    'Crack':'crack','Girdling Roots':'girdling_roots', 'Exposed Roots': 'exposed_roots', 'Recent Trenching':'recent_trenching',
                                    'Cable or Brace':'cable_or_brace','Conflict with Wires':'wire_conflict',
                                    'Conflict with Sidewalk':'sidewalk_conflict','Conflict with Structure':'structure_conflict',
                                    'Conflict with another tree':'tree_conflict','Conflict with Traffic Sign':'sign_conflict'})


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

    return gridReturnData


# st.subheader('Data')
# AgGrid(df)

def getSpeciesTable():
    speciesTable = pd.read_excel(r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\NWspecies060222.xlsx", sheet_name = 'species')
    return speciesTable

speciesTable = getSpeciesTable()

# st.subheader('Species Table')
# AgGrid(speciesTable)

def getOrigin():
    origin = pd.read_excel(r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\NWspecies060222.xlsx", sheet_name = 'origin')
    return origin

df_origin = getOrigin()

# st.subheader('Origin')
# AgGrid(df_origin)

def getEcodistricts():
    gpd_ecodistricts = gpd.read_file(r"C:\Users\HP\Documents\Data\Files\GIS\USDA Tree Maps\OntarioEcodistricts.gpkg")
    return gpd_ecodistricts

gpd_ecodistricts = getEcodistricts()


def getCodes():
    codes = pd.read_excel(r"C:\Users\HP\OneDrive\Neighbourwoods\NWAnalytics\NWspecies060222.xlsx", sheet_name = 'codes')
    return codes

df_codes = getCodes()

df_trees = df_trees.merge(speciesTable.loc[:,['species_code','family', 'genus','species', 'Max DBH', 'invasivity',
    'suitability', 'diversity_level']], how='left')

df_trees=df_trees.rename(columns = {'Max DBH':'max_dbh'})

def origin(df_trees):
    df_trees = df_trees.merge(df_origin.loc[:,['species_code', activeEcodist]], how='left')
    df_trees=df_trees.rename(columns = {activeEcodist:'origin'})

    return df_trees


df_trees['date'] = pd.to_datetime(df_trees['date'], errors='coerce').dt.strftime('%d-%m-%Y')

df_trees = origin(df_trees)

def cpa(cw):
    '''
    calculate crown projection area
    '''
    if pd.isnull(df_trees['crown_width'].iloc[0]):
        cpa = 'n/a'
    
    else:
       cpa = ((cw/2)**2)*3.14
    
    return cpa

df_trees['Crown Projection Area (CPA)'] = df_trees['crown_width'].apply(lambda x: (cpa(x)))

df_trees["Address"] = df_trees.apply(lambda x : str(x["house_number"]) + ' ' +  str(x["street"]), axis=1)


def dbh_class(d):
    
    if d <= 20:
        dbh_class='I'
    elif d <= 40:
        dbh_class='II'
    elif d <= 60:
        dbh_class='III'
    else:
        dbh_class='IV'
            
    return dbh_class

df_trees['DBH class']= df_trees['dbh'].apply(lambda x: dbh_class(x))

def rdbh():
    df_trees['Relative Dbh'] =df_trees.apply(lambda x: 'n/a' if pd.isnull('dbh') else x.dbh/x.max_dbh, axis =1).round(2)

    df_trees.drop('max_dbh', axis=1, inplace=True)

rdbh()
def rdbh_class(d):
    
    if d <= 0.25:
        rdbh_class='I'
    elif d <= 0.50:
        rdbh_class='II'
    elif d <= 0.75:
        rdbh_class='III'
    else:
        rdbh_class='IV'
            
    return rdbh_class

df_trees['Relative DBH Class']= df_trees['Relative Dbh'].apply(lambda x: rdbh_class(x))

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

df_trees[['Latitude', 'Longitude']] = df_trees['xy'].str.split(',', 1, expand=True)

df_trees.drop('xy', axis=1, inplace=True)

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

condition()

df_trees=df_trees.rename(columns = {'tree_name':'Tree Name', 'date': 'Date', 'block':'Block ID',
    'Tree No':'Tree Number','street':'Street','location_code': 'Location Code','ownership_code': 'Ownership Code',
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
    'genus':'Genus', 'species':'Species', 'Relative Dbh': 'Relative DBH', 'origin':'Native', 'suitability':'Species Suitability'
    })


df_trees=df_trees[['Tree Name',	'Description',	'Longitude',	'Latitude',	'Date',
    'Block ID',	'Tree Number',	'Species',	'Genus',	'Family',	'Street',	
    'Address',	'Location Code',	'Ownership Code',	'Number of Stems',	'DBH',	'Hard Surface',
    'Crown Width',	'Ht to Crown Base',	'Total Height',	'Reduced Crown',	'Unbalanced Crown',
    'Defoliation',	'Weak or Yellowing Foliage',	'Dead or Broken Branch',	'Lean',	'Poor Branch Attachment',
    'Branch Scars',	'Trunk Scars',	'Conks',	'Rot or Cavity - Branch',	'Rot or Cavity - Trunk',	'Confined Space',
    'Crack',	'Girdling Roots',	'Exposed Roots',	'Recent Trenching',	'Cable or Brace',	'Conflict with Wires',
    'Conflict with Sidewalk',	'Conflict with Structure',	'Conflict with Another Tree',	'Conflict with Traffic Sign',
    'Comments',	'Crown Projection Area (CPA)',	'Relative DBH',	'Relative DBH Class',	'DBH class',	'Native',
    'Species Suitability',	'Structural Defect',	'Health Defect'
    ]]

# aggFilter(df_trees)

mainTable = aggFilter(df_trees)

# saveDataButton = st.button('Save data as Excel', key='saveData')

# if st.button('Save data as Excel', key='saveData'):

towrite = io.BytesIO()
downloaded_file = mainTable.to_excel(towrite, encoding='utf-8', index=False, header=True)
towrite.seek(0)  # reset pointer
b64 = base64.b64encode(towrite.read()).decode()  # some strings
linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="NwinputData.xlsx">Click here to save your data as an Excel file</a>'
st.markdown(linko, unsafe_allow_html=True) 

