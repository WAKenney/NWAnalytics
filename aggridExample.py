from st_aggrid import AgGrid
import pandas as pd
import streamlit as st

fileName = r"C:\Users\HP\OneDrive\Neighbourwoods\Neighbourwoods neighbourhoods\Beaverbrook\Beaverbrook Neighbourwoods MS 2.6 2017 to 2021.xlsm"
df = pd.read_excel(fileName, sheet_name = "summary", header = 1)

# df = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv')
df_select = AgGrid(df)
