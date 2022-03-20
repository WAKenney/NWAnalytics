import pandas as pd
import streamlit as st
# from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid.shared import GridUpdateMode


df_path = r"C:\Users\HP\OneDrive\Neighbourwoods\Neighbourwoods neighbourhoods\Beaverbrook\Beaverbrook Neighbourwoods MS 2.6 2017 to 2021.xlsm"
df = pd.read_excel(df_path,sheet_name = "summary", header = 1)

gb = GridOptionsBuilder.from_dataframe(df)

gb.configure_pagination()

gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True)



cellsytle_jscode = JsCode(
    """
function(params) {
    if (params.value.includes('yes')) {
        return {
            'color': 'white',
            'backgroundColor': 'darkred'
        }
    } else {
        return {
            'color': 'black',
            'backgroundColor': 'white'
        }
    }
};
"""
)

gb.configure_column("Structural Defect", cellStyle=cellsytle_jscode)




gridOptions = gb.build()


# AgGrid(df, gridOptions=gridOptions)

data = AgGrid(
    df,
    gridOptions=gridOptions,
    # enable_enterprise_modules=True,
    allow_unsafe_jscode=True,
     update_mode=GridUpdateMode.SELECTION_CHANGED
)

selected_rows = data["selected_rows"]
selected_rows = pd.DataFrame(selected_rows)

if len(selected_rows) != 0:
    # fig = px.bar(selected_rows, "rating", color="type")
    fig = px.bar(selected_rows)
    st.plotly_chart(fig)
