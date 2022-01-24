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
    st.title('Information hub')

    # import data as dfs

    # cmsa data
    cmsa_all = pd.read_csv("data/cmsa_combined.csv")
    cmsa_all['total'] = cmsa_all['GAWW-11'] + cmsa_all['GAWW-12'] + cmsa_all['GAWW-14']
    cmsa_all['datetime'] = pd.to_datetime(cmsa_all['datetime'])
    cmsa_per_day = cmsa_all.resample('D', on='datetime').sum()

    # gvb
    dam = pd.read_csv('data/gvb/gvb_dam.csv')
    dam['datetime'] = pd.to_datetime(dam['datetime'])
    dam['total'] = dam['checkin'] + dam['checkout']
    dam_per_day = dam.resample('D', on='datetime').sum()

    nieuwmarkt = pd.read_csv('data/gvb/gvb_nieuwmarkt.csv')
    nieuwmarkt['datetime'] = pd.to_datetime(nieuwmarkt['datetime'])
    nieuwmarkt['total'] = nieuwmarkt['checkin'] + nieuwmarkt['checkout']
    nieuwmarkt_per_day = nieuwmarkt.resample('D', on='datetime').sum()

    # knmi
    knmi = pd.read_csv('data/knmi/knmi_for_baseline.csv')
    knmi['datetime'] = pd.to_datetime(knmi['datetime'])
    knmi_per_day = knmi.resample('D', on='datetime').sum()

    # stations map
    stations = {'Dam': dam_per_day, 'Nieuwmarkt': nieuwmarkt_per_day}

    with st.container():
        col_a, col_b, col_empty = st.columns([0.2, 0.2, 0.6])
        with col_a:
            start_dt = st.date_input('Start date', value=cmsa_per_day.index.min())
        with col_b:
            end_dt = st.date_input('End date', value=cmsa_per_day.index.max())

        # COMBINATION PLOT
        st.header("CMSA Passengers per day")

        fig_cmsa = go.Figure()
        fig_cmsa.add_trace(
            go.Scatter(
                x=cmsa_per_day.loc[start_dt:end_dt].index,
                y=cmsa_per_day.loc[start_dt:end_dt]['total'],
                text='total',
                name='passengers by day'))

        fig_cmsa.update_layout(
            margin=dict(l=20, r=20, t=30, b=20)
        )

        fig_cmsa.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        st.plotly_chart(fig_cmsa, use_container_width=True)

        # GVB PLOT
        st.header("GVB")

        col_a, col_b, col_empty = st.columns([0.2, 0.2, 0.6])
        with col_a:
            radio_gvb = st.radio("", ('checkin', 'checkout', 'total'))
        with col_b:
            options_gvb = st.multiselect(
                'Stations',
                ['Dam', 'Nieuwmarkt'], 'Dam')

        fig_gvb = go.Figure()
        for i in options_gvb:
            fig_gvb.add_trace(
                go.Scatter(
                    x=stations[i].loc[start_dt:end_dt].index,
                    y=stations[i].loc[start_dt:end_dt][radio_gvb],
                    #   text = column,
                    name=str(i) + " " + str(radio_gvb)))

        fig_gvb.update_layout(
            title="GVB data",
            margin=dict(l=20, r=20, t=35, b=20),
            width=400,
            height=200,
        )
        fig_gvb.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
        fig_gvb['data'][0]['showlegend'] = True
        st.plotly_chart(fig_gvb, use_container_width=True)

        # KNMI PLOT
        knmi_mapping = {'Temperature': 'temperature', 'Precipitation': 'precipitation_h', 'Cloud cover': 'cloud_cover',
                        'Wind speed': 'wind_speed'}
        st.header("KNMI")
        knmi_radio = st.radio("", ['Temperature', 'Precipitation', 'Cloud cover', 'Wind speed'])

        fig_knmi = go.Figure()
        fig_knmi.add_trace(
            go.Scatter(
                x=knmi_per_day.loc[start_dt:end_dt].index,
                y=knmi_per_day.loc[start_dt:end_dt][knmi_mapping[knmi_radio]],
                #       text = column,
                name=knmi_radio
            ))

        fig_knmi.update_layout(
            title="KNMI data",
            margin=dict(l=20, r=20, t=35, b=20),
            width=400,
            height=200,
        )

        fig_knmi['data'][0]['showlegend'] = True
        st.plotly_chart(fig_knmi, use_container_width=True)

    st.header("Insights")
