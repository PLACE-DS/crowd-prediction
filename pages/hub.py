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


def app():
    st.title('Historical information hub')

    #import data as dfs

    #cmsa data
    cmsa_all = pd.read_csv("data/cmsa_combined.csv")
    cmsa_all['total'] = cmsa_all['GAWW-11'] + cmsa_all['GAWW-12'] + cmsa_all['GAWW-14']
    cmsa_all['datetime'] = pd.to_datetime(cmsa_all['datetime'])
    cmsa_per_day = cmsa_all.resample('D', on='datetime').sum()

    #gvb
    dam = pd.read_csv('data/gvb/gvb_dam.csv')
    dam['datetime'] = pd.to_datetime(dam['datetime'])
    dam_per_day = dam.resample('D', on='datetime').sum()

    nieuwmarkt = pd.read_csv('data/gvb/gvb_nieuwmarkt.csv')
    nieuwmarkt['datetime'] = pd.to_datetime(nieuwmarkt['datetime'])
    nieuwmarkt_per_day = nieuwmarkt.resample('D', on='datetime').sum()


    #knmi
    knmi = pd.read_csv('data/knmi/knmi_for_baseline.csv')
    knmi['datetime'] = pd.to_datetime(knmi['datetime'])
    knmi_per_day = knmi.resample('D', on='datetime').sum()

    column1, column2 = st.columns(2)

    #make plots

    with column1:
        st.header("CMSA + other data sources")
        date_start = '2020-09-01'
        date_end = '2020-09-30'
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=cmsa_per_day.loc[date_start:date_end].index,
                y=cmsa_per_day.loc[date_start:date_end]['total'],
                name ='passengers by day'))
        fig.add_trace(
            go.Scatter(
                x=dam_per_day.loc[date_start:date_end].index,
                y=dam_per_day.loc[date_start:date_end]['checkin'] + dam_per_day.loc[date_start:date_end]['checkout'],
                name="dam checkins + checkouts per day"))

        st.plotly_chart(fig)

    with column2:
        st.header("Historical other data sources ")
