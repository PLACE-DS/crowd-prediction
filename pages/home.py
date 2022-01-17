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
    w1, w2, w3, w4, w5, w6 = st.columns(6)
    st.title('Homepage')
    w1.markdown("![weather icon](" + icon + ")")
    w2.metric("Temperature", str(weather['current']['temp_c']) + " °C")
    w3.metric("Wind", str(weather['current']['wind_kph'])+ " kph")

    #column1, column2 = st.columns(2)
    column1, column2 = st.columns([3,2])

    with column1:
        st.header("Prediction view")
        #st.map(locations_df, zoom=14.5)
        map = get_map()
        st.pydeck_chart(map)

        day = st.slider('Days ahead', 0, 7, 1)
        hour = st.slider('Hour of the day:', value=datetime.time(00, 00, 00),
                              min_value=datetime.time(00, 00, 00),
                              max_value=datetime.time(23, 45, 00),
                              step=datetime.timedelta(minutes=15),
                              format='H:mm')
        prediction_date = datetime.timedelta(days=day) + datetime.date.today()
        st.write("Prediction for day: ", prediction_date, ", at: ", hour)

    with column2:
        st.header("Overcrowdedness")
        crowds = get_crowd()
        for loc in crowds:
            st.subheader('LOCATION: ' + loc)
            st.write(crowds[loc]['yellow'])
            st.write(crowds[loc]['red'])



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

def get_map():
    location1_df = pd.DataFrame([[52.374611, 4.899833]], columns=['lat', 'lon'])
    location2_df = pd.DataFrame([[52.373883, 4.898653]], columns=['lat', 'lon'])
    location3_df = pd.DataFrame([[52.373571, 4.898272]], columns=['lat', 'lon'])

    color_red = '[255,0,0, 160]' 
    red = '[255,0,0]'
    color_yellow = '[255,255,0, 160]'
    yellow = '[255,255,0]'
    color_green = '[0,255,0, 160]'
    green = '[0,255,0]'
    st.write(green.replace(']',',160]'))

    # gg = get_crowd()


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
                get_color=color_red,
                get_radius=25,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=color_yellow,
                get_radius=25,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=color_green,
                get_radius=25,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=red,
                get_radius=10,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=yellow,
                get_radius=10,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=green,
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
        yellow_forecast = loc_forecast[loc_forecast['prediction'] > loc_info['crowd_threshold_low'][ind]]
        if yellow_forecast.shape[0] > 0:
            yellow_forecast = yellow_forecast[yellow_forecast['prediction'] < loc_info['crowd_threshold_high'][ind]]

        # Get the times with red forecast:
        red_forecast = loc_forecast[loc_forecast['prediction'] > loc_info['crowd_threshold_high'][ind]]

        crowds[loc] = {'yellow': yellow_forecast, 'red':red_forecast}

    return crowds