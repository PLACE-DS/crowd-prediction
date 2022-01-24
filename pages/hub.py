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
        st.markdown('---')
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
        st.markdown('---')
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

        st.markdown('---')
        st.header("Stringency")
        avg_passengers_covid(cmsa_all, st)

        st.markdown('---')
        st.header("Hourly")
        avg_hourly_passengers_bar(cmsa_all, st)

        st.markdown('---')
        st.header("Daily")
        col_a, col_empty = st.columns([0.2, 0.8])
        with col_a:
            radio_daily = st.radio("", ('all-time', 'last month'))
        avg_daily_passengers_bar(cmsa_all, st, radio_daily == 'last month')

        st.markdown('---')
        st.header("Monthly")
        col_a, col_empty = st.columns([0.2, 0.8])
        with col_a:
            radio_monthly = st.radio("", ('all-time', 'last year'))
        avg_monthly_passengers_bar(cmsa_all, st, radio_monthly == 'last year')






def avg_daily_passengers_bar(cb, st, last_month=False):
    week_days = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    frame = cb.set_index('datetime')
    frame['weekday'] = frame.index.day_name()
    if last_month:
        frame = frame[frame.index > '2021-12-01']
    frame = frame[['weekday', 'GAWW-11','GAWW-12', 'GAWW-14']].groupby(by='weekday').mean().reindex(week_days)
    f = px.bar(frame, x=frame.index, y=['GAWW-11','GAWW-12', 'GAWW-14'], barmode='group',
               title='average passengers per day' +
                     (' (all-time)' if not last_month else ' (last month)' ))
    st.plotly_chart(f, use_container_width=True)

def avg_monthly_passengers_bar(cb, st, last_year=False):
    months = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    frame = cb.set_index('datetime')
    if last_year:
        frame = frame[frame.index > '2021-01-01']
    frame['month'] = frame.index.month_name()
    frame = frame[['month', 'GAWW-11','GAWW-12', 'GAWW-14']].groupby(by='month').mean().reindex(months)
    f = px.bar(frame, x=frame.index, y=['GAWW-11','GAWW-12', 'GAWW-14'], barmode='group',
               title='average passengers per month' +
                     (' (all-time)' if not last_year else ' (last year)' ))
    st.plotly_chart(f, use_container_width=True)

def avg_hourly_passengers_bar(cb, st):
    hours = [f'{t:02}:00' for t in (list(range(5,24))+ list(range(0,5)))]
    frame = cb.set_index('datetime')
    if False:
        frame = frame[frame.index > '2021-01-01']

    frame['hour'] = frame.index.hour
    frame = frame[['hour', 'GAWW-11','GAWW-12', 'GAWW-14']].groupby(by='hour').mean().reindex(list(range(5,24))+ list(range(0,5)))
    frame.index = hours
    f = px.bar(frame, x=frame.index, y=['GAWW-11','GAWW-12', 'GAWW-14'], barmode='group',
               title='average passengers per hour' +
                     (' (all-time)' if not False else ' (last year)' ))
    st.plotly_chart(f, use_container_width=True)


def avg_passengers_covid(cb, st):
    filt = (4*24*7)-1

    # create rolling avgs and inv stringency
    cb['SMA7_11'] = np.convolve(np.pad(cb['GAWW-11'], (335,335), mode='edge'), np.ones(filt) / filt, mode='valid')
    cb['SMA7_12'] = np.convolve(np.pad(cb['GAWW-12'], (335,335), mode='edge'), np.ones(filt) / filt, mode='valid')
    cb['SMA7_14'] = np.convolve(np.pad(cb['GAWW-14'], (335,335), mode='edge'), np.ones(filt) / filt, mode='valid')
    cb['inv_cov_stringency'] = (100 - cb.stringency_index)

    # Create figure with secondary y-axis
    fig_cov = make_subplots(specs=[[{"secondary_y": True}]])
    fig_cov.add_trace(go.Scatter(x=cb.index, y=cb.SMA7_11, name="GAWW-11 7-day m.avg."))
    fig_cov.add_trace(go.Scatter(x=cb.index, y=cb.SMA7_12, name="GAWW-12 7-day m.avg."))
    fig_cov.add_trace(go.Scatter(x=cb.index, y=cb.SMA7_14, name="GAWW-14 7-day m.avg."))
    fig_cov.add_trace(
        go.Scatter(x=cb.index, y=cb.inv_cov_stringency, name="inv. stringency index", line=dict(
            color='black',
            width=2)),
        secondary_y=True,
    )

    # plotly manual axis adjustments
    fig_cov.update_yaxes(title_text="7-Day moving average crowd count", secondary_y=False)
    fig_cov.update_yaxes(title_text="Inverse stringency index", showgrid=False, secondary_y=True)
    fig_cov.update
    fig_cov.update_layout(
        title_text="Average crowdedness vs. Covid stringency <br><sup>Inverse Stringency Index from 0 (strictest) to 100 (relaxed)</sup>"
    )

    st.plotly_chart(fig_cov, use_container_width=True)