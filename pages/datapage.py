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
    columns = cmsa_all.columns[4:]
    st.title('Data and Code')

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
    check_columns = [st.checkbox(i, key=i) for i in columns]
    checked_sensors = [stock for stock, checked in zip(sensors, check_sensors) if checked]
    checked_columns = [stock for stock, checked in zip(columns, check_columns) if checked]
    st.write(checked_sensors, checked_columns)
    # st.checkbox('KNMI')
    # st.checkbox('GVB')s
    # st.checkbox('Covid')
    # st.checkbox('Tourism')

    def convert_df(df):
        return df.to_csv()

    downloadcolumns = ['datetime'] + list(checked_sensors) + list(checked_columns)
    st.write(downloadcolumns)

    downloadcsv = convert_df(cmsa_all[downloadcolumns])

    st.download_button(label = 'download .csv', data=downloadcsv, mime='text/csv')

