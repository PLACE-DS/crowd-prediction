import streamlit as st
import requests as re 
import streamlit as st
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import pydeck as pdk
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from st_aggrid import AgGrid

st.set_page_config(layout="wide")

# Analyzed sensors:
locations = {'GAWW-11': [52.374611, 4.899833],
             'GAWW-12': [52.373883, 4.898653],
             'GAWW-14': [52.373571, 4.898272]}

def app():
    #with st.container():
    first_forecast, last_forecast = get_dates()
    w1, w2, w3, w4, w5, w6 = st.columns(6)
    #st.title('Homepage')
    w1.markdown("![weather icon](" + icon + ")")
    w2.metric("Temperature", str(weather['current']['temp_c']) + " °C")
    w3.metric("Wind", str(weather['current']['wind_kph'])+ " kph")

    #column1, column2 = st.columns(2)
    column1, column2 = st.columns([3,2])

    with column1:
        st.header("Prediction view")

        #display = st.select_slider('', options=['Map', 'Plot'])
        #st.write('You are seeing a: ', display)

        display = st.selectbox('What do you want to see? map/plot',
            ('Map', 'Plot'))

        if display == 'Map':
            #day = st.slider('Days ahead', 0, 7, 1)
            day_pred = st.slider('Prediction day:', value=first_forecast,
                                    min_value=first_forecast,
                                    max_value=last_forecast,
                                    step=datetime.timedelta(days=1))
            hour = st.slider('Hour of the day:', value=datetime.time(00, 00, 00),
                                    min_value=datetime.time(00, 00, 00),
                                    max_value=datetime.time(23, 45, 00),
                                    step=datetime.timedelta(minutes=15),
                                    format='H:mm')
            #prediction_date = datetime.timedelta(days=day) + datetime.date.today()

            #st.map(locations_df, zoom=14.5)
            map = get_map(day_pred, hour)
            st.pydeck_chart(map)

            st.write("Prediction for day: ", day_pred.date(), ", at: ", hour)

        else:
            get_plot()

    with column2:
        st.header("Overcrowdedness")
        crowds = get_crowd()
        for loc in crowds:
            st.subheader('LOCATION: ' + loc)
            st.write(crowds[loc]['yellow'])
            st.write(crowds[loc]['red'])

        st.header("Public transport")



# GET THE CURRENT WEATHER IN AMSTERDAM:
r = re.get('http://api.weatherapi.com/v1/current.json?key=16a275e088724a3eba1143500221201&q=Amsterdam&aqi=no')
weather = r.json()
icon = "http:" + str(weather['current']['condition']['icon'])
#st.write("Current temperature in Amsterdam:",weather['current']['temp_c'],"degrees Celsius")
#st.markdown("![weather icon](" + icon + ")")

# FORECASTS FOR THE 3 LOCATIONS:
forecast1 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-11.csv')
forecast2 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-12.csv')
forecast3 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-14.csv')
sensors_info = pd.read_csv('data/sensors-info.csv')

# SENSORS LOCATION:
# CMSA-GAWW-11 - 52.374611, 4.899833 (52°22'28.6"N 4°53'59.4"E)
# CMSA-GAWW-12 - 52.373883, 4.898653 (52°22'26.0"N 4°53'55.2"E)
# CMSA-GAWW-14 - 52.373571, 4.898272 (52°22'24.9"N 4°53'53.8"E)
locations_df = pd.DataFrame(
        [[52.374611, 4.899833], [52.373883, 4.898653], [52.373571, 4.898272]],
        columns=['lat', 'lon'])

def get_map(day_pred, hour):
    location1_df = pd.DataFrame([[52.374611, 4.899833]], columns=['lat', 'lon'])
    location2_df = pd.DataFrame([[52.373883, 4.898653]], columns=['lat', 'lon'])
    location3_df = pd.DataFrame([[52.373571, 4.898272]], columns=['lat', 'lon'])

    loc_colors = get_colors(day_pred, hour)
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=52.374,
            longitude=4.899,
            zoom=14,
            height=400,
            width='100%',
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-11'].replace(']',',160]'),
                get_radius=25,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-12'].replace(']',',160]'),
                get_radius=25,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-14'].replace(']',',160]'),
                get_radius=25,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-11'],
                get_radius=10,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-12'],
                get_radius=10,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-14'],
                get_radius=10,
            ),
        ],
    )

    return map

def get_crowd():
    crowds = {}
    for ind, loc in enumerate(locations):
        loc_info = sensors_info[sensors_info['objectnummer']=='CMSA-'+loc]
        loc_forecast = pd.read_csv('experiments/fake_forecasts_for_frontend/'+ loc +'.csv')

        # Get the times with yellow forecast:
        yellow_forecast = loc_forecast[loc_forecast['prediction'] > loc_info['crowd_threshold_low'][ind]-500]
        if yellow_forecast.shape[0] > 0:
            yellow_forecast = yellow_forecast[yellow_forecast['prediction'] < loc_info['crowd_threshold_high'][ind]-600]

        # Get the times with red forecast:
        red_forecast = loc_forecast[loc_forecast['prediction'] > loc_info['crowd_threshold_high'][ind]-600]
        crowds[loc] = {'yellow': yellow_forecast, 'red':red_forecast}

    return crowds

def get_colors(day_pred, hour):
    red = '[255,0,0]'
    yellow = '[255,255,0]'
    green = '[0,255,0]'

    crowds = get_crowd()
    date = datetime.datetime.combine(day_pred, hour)
    loc_colors = {}

    for ind, loc in enumerate(locations):
        if str(date) in crowds[loc]['red'].datetime.tolist():
            loc_colors[loc] = red
        elif str(date) in crowds[loc]['yellow'].datetime.tolist():
            loc_colors[loc] = yellow
        else:
            loc_colors[loc] = green

    return loc_colors

def get_dates():
    first_forecast_str = forecast1['datetime'].iloc[0]
    first_forecast = datetime.datetime.strptime(first_forecast_str, '%Y-%m-%d %H:%M:%S')
    last_forecast_str = forecast1['datetime'].iloc[-1]
    last_forecast = datetime.datetime.strptime(last_forecast_str, '%Y-%m-%d %H:%M:%S')
    # st.write(first_forecast.date())
    # st.write(last_forecast.date())

    return first_forecast, last_forecast

def get_plot():
    all_forecasts = forecast1.drop(['upper', 'lower'], axis=1)
    all_forecasts = all_forecasts.rename(columns={'prediction': 'GAWW-11'})
    all_forecasts['GAWW-12'] = forecast2.prediction
    all_forecasts['GAWW-14'] = forecast3.prediction
    all_forecasts['total'] = all_forecasts['GAWW-11'] + all_forecasts['GAWW-12'] + all_forecasts['GAWW-14']
    all_forecasts['datetime2']=pd.to_datetime(all_forecasts.datetime)
    #all_forecasts['datetime2'] = all_forecasts.index

    fig = go.Figure()
    loc_radio = st.radio("Location", ("All", "GAWW-11", "GAWW-12", "GAWW-14"))
    if loc_radio == 'All':
        for ind, loc in enumerate(locations):
            fig.add_trace(
                go.Scatter(
                    x=all_forecasts.datetime2,
                    y=all_forecasts[loc],
                    text = loc,
                    name = 'crowd'))
    else:
        fig.add_trace(
            go.Scatter(
                x=all_forecasts.datetime2,
                y=all_forecasts[loc_radio],
                text = loc_radio,
                name = 'crowd'))
        # fig.add_trace(
            # go.Scatter(
                # ADD DASHED THRESHOLDS
                # ))

    fig.update_layout(
        title="7 Day prediction",
        margin=dict(l=20, r=20, t=30, b=20),
        # width = 550,
        # height = 400
        )

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
        ))

    st.plotly_chart(fig,use_container_width=True)


def convert_date(row):
    gg = datetime.datetime.strptime(row['datetime2'], '%Y-%m-%d %H:%M:%S')
    return gg