import streamlit as st
import requests as re
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# cmsa_all = pd.read_csv("data/cmsa_combined.csv")
# cmsa_all['total'] = cmsa_all['GAWW-11'] + cmsa_all['GAWW-12'] + cmsa_all['GAWW-14']
# cmsa_all['datetime'] = pd.to_datetime(cmsa_all['datetime'])
# cmsa_per_day = cmsa_all.resample('D', on='datetime').sum()
# columns = [cmsa_all.columns]

def app():
    cmsa_all = pd.read_csv("data/cmsa_combined.csv")
    cmsa_all['total'] = cmsa_all['GAWW-11'] + cmsa_all['GAWW-12'] + cmsa_all['GAWW-14']
    cmsa_all['datetime'] = pd.to_datetime(cmsa_all['datetime'])
    cmsa_per_day = cmsa_all.resample('D', on='datetime').sum()
    sensors = cmsa_all.columns[1:4]
    columns = cmsa_all.columns[6:]
    knmi_columns = cmsa_all.columns[19:]
    gvb_columns = cmsa_all.columns[7:10]
    tourism_columns = cmsa_all.columns[11:15]
    covid_columns = cmsa_all.columns[16:18].tolist()
    covid_columns.append(cmsa_all.columns[6])
    

    st.title('Data and Code')
    st.markdown('Use the date selector and column checkboxes to export the data of your choice.')

    start_dt = st.date_input('Start date',
        value=cmsa_per_day.index.min(),
        min_value = cmsa_per_day.index.min(),
        max_value = cmsa_per_day.index.max())

    end_dt = st.date_input('End date',
        value=cmsa_per_day.index.max(),
        min_value = cmsa_per_day.index.min(),
        max_value = cmsa_per_day.index.max())

    st.header('Select sensors')
    check_sensors = [st.checkbox(i, key=i) for i in sensors]
    st.header('Select metadata')
    all_metadata = st.checkbox('Select all features (overrides settings below)')

    with st.expander('Covid'):
        check_covid = [st.checkbox(i, key=i) for i in covid_columns]

    with st.expander('GVB'):
        check_gvb = [st.checkbox(i, key=i) for i in gvb_columns]

    with st.expander('KNMI'):
        check_knmi = [st.checkbox(i, key=i) for i in knmi_columns]

    with st.expander('Tourism'):
        check_tourism = [st.checkbox(i, key=i) for i in tourism_columns]

    #check_columns = [st.checkbox(i, key=i) for i in columns]
    checked_sensors = [stock for stock, checked in zip(sensors, check_sensors) if checked]
    checked_covid = [stock for stock, checked in zip(covid_columns, check_covid) if checked or all_metadata]
    checked_gvb = [stock for stock, checked in zip(gvb_columns, check_gvb) if checked or all_metadata]
    checked_knmi = [stock for stock, checked in zip(knmi_columns, check_knmi) if checked or all_metadata]
    checked_tourism = [stock for stock, checked in zip(tourism_columns, check_tourism) if checked or all_metadata]

    def convert_df(df):
        return df.to_csv()

    downloadcolumns = ['datetime'] + list(checked_sensors) + list(checked_covid) + list(checked_gvb) + list(checked_knmi) + list(checked_tourism)
    df_to_download = cmsa_all[downloadcolumns]
    df_to_download['datetime'] = pd.to_datetime(df_to_download['datetime'])
    df_to_download = df_to_download[(df_to_download['datetime'].dt.date > start_dt) & (df_to_download['datetime'].dt.date < end_dt)]

    downloadcsv = convert_df(df_to_download)
    

    st.download_button(label = 'download .csv', data=downloadcsv,  mime='text/csv')
