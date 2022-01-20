from tracemalloc import start
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

# Analyzed sensors:
locations = {'GAWW-11': [52.374611, 4.899833],
             'GAWW-12': [52.373883, 4.898653],
             'GAWW-14': [52.373571, 4.898272]}

def app():
    with st.container():
        first_forecast, last_forecast = get_dates()
        #st.title('Homepage')

        get_weather()
        #column1, column2 = st.columns(2)
        column1, column2 = st.columns([3,2])

        with column1:
            st.header("Prediction view")

            #display = st.select_slider('', options=['Map', 'Plot'])
            display = st.radio("What do you want to see?", ("Map", "Plot"))
            #st.write('You are seeing a: ', display)

            #display = st.selectbox('What do you want to see? map/plot',
            #    ('Plot', 'Map'))

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
            st.write('Predicted overcrowded moments for the next 7 days on the 3 locations:')
            display_crowds()

    #st.markdown('', unsafe_allow_html=True)


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

locations_names = {'GAWW-11': 'Korte Niezel', 'GAWW-12': 'Oudekennissteeg', 'GAWW-14': 'Oudezijds Voorburgwal 91'}

def get_weather():
    try:
        # GET THE CURRENT WEATHER IN AMSTERDAM:
        r = re.get('http://api.weatherapi.com/v1/current.json?key=16a275e088724a3eba1143500221201&q=Amsterdam&aqi=no')
        weather = r.json()
        icon = "http:" + str(weather['current']['condition']['icon'])
        #st.write("Current temperature in Amsterdam:",weather['current']['temp_c'],"degrees Celsius")
        #st.markdown("![weather icon](" + icon + ")")

        w1, w2, w3, w4, w5, w6 = st.columns(6)
        w1.markdown("![weather icon](" + icon + ")")
        w2.metric("Temperature", str(weather['current']['temp_c']) + " °C")
        w3.metric("Wind", str(weather['current']['wind_kph'])+ " kph")
    except:
        # In case there's no internet connection
        pass

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
            zoom=15,
            height=400,
            width='100%',
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-11'].replace(']',',160]'),
                get_radius=18,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-12'].replace(']',',160]'),
                get_radius=18,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-14'].replace(']',',160]'),
                get_radius=18,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-11'],
                get_radius=7,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-12'],
                get_radius=7,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-14'],
                get_radius=7,
            ),
        ],
    )

    return map

def get_crowd():
    crowds = {}
    crowds_combined = {}
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



        # MERGE OVERCROWDED FORECASTS:
        yellow = yellow_forecast.drop(['upper', 'lower'], axis=1)
        yellow['overcrowdedness'] = 'orange'
        yellow.set_index('datetime')

        red = red_forecast.drop(['upper', 'lower'], axis=1)
        red['overcrowdedness'] = 'red'
        red.set_index('datetime')

        merged = pd.concat([yellow, red])
        merged = merged.sort_values(by=['datetime'])

        merged['start'] = pd.to_datetime(merged['datetime'], format='%Y-%m-%d %H:%M:%S', errors='ignore')
        merged['end'] = pd.to_datetime(merged['datetime'], format='%Y-%m-%d %H:%M:%S', errors='ignore')

        rowlist = []
        cut_row = None
        for row in merged.itertuples():
            if cut_row is None:
                cut_row = row._asdict()
            elif not(cut_row.get('overcrowdedness') == row.overcrowdedness):
                rowlist.append(cut_row)
                cut_row = row._asdict()
            elif (row.start - cut_row.get('end'))< datetime.timedelta(minutes=16):
                cut_row['end'] = row.end
            else:
                rowlist.append(cut_row)
                cut_row = row._asdict()
        rowlist.append(cut_row)
        combine_merged = pd.DataFrame.from_dict(rowlist)

        crowds_combined[loc] = combine_merged

    return crowds, crowds_combined

def display_crowds():
    crowds, crowds_combined = get_crowd()
    for loc in crowds:
        st.subheader(locations_names[loc])
        if 'Index' in crowds_combined[loc].columns:
            combined = crowds_combined[loc].drop(['Index', 'datetime', 'prediction'], axis=1)
            combined = crowds_combined[loc]
            combined['date'] = combined.start.dt.date
            combined['start_time'] = combined.start.dt.time
            combined['end_time'] = combined.end.dt.time

            for date in combined.date.unique():
                #st.write(date.strftime("%d-%m-%Y"))
                st.markdown('<p style="font-weight: bold;">' + date.strftime("%d-%m-%Y") + '</p>', unsafe_allow_html=True)
                dff = combined[combined['date'] == date]
                for row in dff.itertuples():
                    if row.start_time == row.end_time:
                        end = row.end + datetime.timedelta(minutes=15)
                        end = end.time()
                    else:
                        end = row.end_time
                    #if row.start_time == row.end_time:
                      #   row.end_time = (row.end + datetime.timedelta(minutes=15))
                    #st.markdown('<i class="fas fa-circle" style="color: red;">', unsafe_allow_html=True)
                    # st.write('From ', row.start_time.strftime("%H:%M"), ' to ', end.strftime("%H:%M"))
                    st.markdown('<a style="color: '+ row.overcrowdedness +'; font-weight: 900; padding-left: 15px"> O</a>  From '+  row.start_time.strftime("%H:%M") + ' to ' + end.strftime("%H:%M"), unsafe_allow_html=True)
        else:
            st.write('No overcrowded moments for this location in the next 7 days')



def get_colors(day_pred, hour):
    red = '[255,0,0]'
    yellow = '[255,255,0]'
    green = '[0,255,0]'

    crowds, _ = get_crowd()
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

    # Add the thresholds
    for ind, loc in enumerate(locations):
        loc_info = sensors_info[sensors_info['objectnummer']=='CMSA-'+loc]
        all_forecasts[loc+'_th_low'] = loc_info['crowd_threshold_low'][ind]-500
        all_forecasts[loc+'_th_high'] = loc_info['crowd_threshold_high'][ind]-600

    colors_list = ['#D31222', '#69292E', '#445769']
    colors_dict = {'GAWW-11': '#D31222', 'GAWW-12': '#69292E', 'GAWW-14': '#445769'}

    fig = go.Figure()
    # loc_radio = st.radio("Location", ("All", "GAWW-11", "GAWW-12", "GAWW-14"))

    options_loc = st.multiselect('Select locations', ["GAWW-11", "GAWW-12", "GAWW-14"], ["GAWW-11", "GAWW-12", "GAWW-14"])


    if len(options_loc) > 0:
        for ind, loc in enumerate(options_loc):
            fig.add_trace(
                go.Scatter(
                    x=all_forecasts.datetime2,
                    y=all_forecasts[loc],
                    text = loc,
                    name = loc,
                    line_color = colors_dict[loc],
                    line_width=2))
            if len(options_loc) == 1:
                fig.add_trace(
                    go.Scatter(
                        x=all_forecasts.datetime2,
                        y=all_forecasts[loc+'_th_low'],
                        line_color = colors_dict[loc],
                        text = 'Low threshold',
                        name = 'Low threshold',
                        line_width=0.5))

                fig.add_trace(
                    go.Scatter(
                        x=all_forecasts.datetime2,
                        y=all_forecasts[loc+'_th_high'],
                        line_color = colors_dict[loc],
                        text = 'High threshold',
                        name = 'High threshold',
                        line_width=0.5))
    else:
        pass


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