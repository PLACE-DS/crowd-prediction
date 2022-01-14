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

    start_dt = st.date_input('Start date', value=cmsa_per_day.index.min())
    end_dt = st.date_input('End date', value=cmsa_per_day.index.max())

    #make plots

    with column1:
        st.header("CMSA + other data sources")

        trace2radio = st.radio("Second trace", ("GVB", "KNMI", "Parking", "Covid-19 cases", "Events"))
        if trace2radio == 'GVB':
            trace2 = dam_per_day
            column = 'checkin'
            tracetitle = "dam checkins per day"
        elif trace2radio == 'KNMI':
            trace2 = knmi_per_day
            column = 'temperature'
            tracetitle = 'temperature per day'


        date_start = '2020-09-01'
        date_end = '2020-09-30'

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=cmsa_per_day.loc[start_dt:end_dt].index,
                y=cmsa_per_day.loc[start_dt:end_dt]['total'],
                text = 'total',
                                name ='passengers by day'))
        fig.add_trace(
            go.Scatter(
                x=trace2.loc[start_dt:end_dt].index,
                y=trace2.loc[start_dt:end_dt][column],
                text = column,
                name= tracetitle))

        fig.update_layout(
            title="Sensor data + other source",
            margin=dict(l=20, r=20, t=30, b=20),
            width = 550,
            height = 400)
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
            ))

        st.plotly_chart(fig)


    with column2:
        st.header("Historical other data sources ")


        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=dam_per_day.loc[start_dt:end_dt].index,
                y=dam_per_day.loc[start_dt:end_dt]['checkin'],
                text = column,
                name= tracetitle))
        fig2.update_layout(
            title="GVB data",
            margin=dict(l=20, r=20, t=35, b=20),
            width = 400,
            height = 200,
            )


        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=knmi_per_day.loc[start_dt:end_dt].index,
                y=knmi_per_day.loc[start_dt:end_dt]['temperature'],
                text = column,
                name= tracetitle))
        fig3.update_layout(
            title="KNMI data",
            margin=dict(l=20, r=20, t=35, b=20),
            width = 400,
            height = 200,
            )

        st.plotly_chart(fig2)

        st.plotly_chart(fig3)
