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

# FORECASTS FOR THE 3 LOCATIONS:
forecast1 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-11.csv')
forecast2 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-12.csv')
forecast3 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-14.csv')
sensors_info = pd.read_csv('data/sensors-info.csv', sep=';')


def get_dates():
    first_forecast_str = forecast1['datetime'].iloc[0]
    first_forecast = datetime.datetime.strptime(first_forecast_str, '%Y-%m-%d %H:%M:%S')
    last_forecast_str = forecast1['datetime'].iloc[-1]
    last_forecast = datetime.datetime.strptime(last_forecast_str, '%Y-%m-%d %H:%M:%S')

    return first_forecast, last_forecast


first_forecast, last_forecast = get_dates()

day_pred = first_forecast
hour = datetime.time(12, 00, 00)
display = 'Map'
horizon = '3 days'


def app():
    with st.container():
        # st.title('Homepage')

        col_title, w1, w2, w3 = st.columns([0.8, 0.15, 0.15, 0.15])
        get_weather(w1, w2, w3)

        st.markdown("---")

        col_map, col_plot, col_empty = st.columns([0.1, 0.1, 0.8])
        global display
        if col_map.button("📍 Map view ", key='map_button', on_click=style_button_row, kwargs={'clicked_button_ix': 'Map'}):
            display = 'Map'

        if col_plot.button("📈 Plot view ", key='plot_button', on_click=style_button_row,
                     kwargs={'clicked_button_ix': 'Plot'}):
            display = 'Plot'


        column1, spacer, column2 = st.columns([5, 0.3, 2])
        with column1:
            st.header("Prediction view")

            # display = st.select_slider('', options=['Map', 'Plot'])
            # st.write('You are seeing a: ', display)

            # display = st.selectbox('What do you want to see? map/plot',
            #    ('Plot', 'Map'))

            if display == 'Map':
                get_map_prediction()
            elif display == 'Plot':
                get_plot_prediction()

        with column2:
            st.header("Overcrowdedness")
            st.write('Predicted overcrowded moments for the next 7 days on the 3 locations:')
            st.write(' 🔴 **Overcrowded** (95<sup>th</sup> percentile)', unsafe_allow_html=True)
            st.write(' 🟡 **Crowded** (90<sup>th</sup> percentile)', unsafe_allow_html=True)
            st.markdown('---')
            get_crowded_moments()


def style_button_row(clicked_button_ix):
    clicked_style = """
    div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
        border-color: rgb(255, 75, 75);
        color: rgb(255, 75, 75);
        box-shadow: rgba(255, 75, 75, 0.5) 0px 0px 0px 0.2rem;
        outline: currentcolor none medium;
    }
    """
    unclicked_style = """
    div[data-testid*="stHorizontalBlock"] > div:nth-child(%(nth_child)s):nth-last-child(%(nth_last_child)s) button {
        pointer-events: none;
        cursor: not-allowed;
        opacity: 0.65;
        filter: alpha(opacity=65);
        -webkit-box-shadow: none;
        box-shadow: none;
    }
    """
    st.markdown(f"<style>{clicked_style}</style>", unsafe_allow_html=True)


day_pred = first_forecast
hour = datetime.time(12, 00, 00)

# SENSORS LOCATION:
# CMSA-GAWW-11 - 52.374611, 4.899833 (52°22'28.6"N 4°53'59.4"E)
# CMSA-GAWW-12 - 52.373883, 4.898653 (52°22'26.0"N 4°53'55.2"E)
# CMSA-GAWW-14 - 52.373571, 4.898272 (52°22'24.9"N 4°53'53.8"E)
locations_df = pd.DataFrame(
    [[52.374611, 4.899833], [52.373883, 4.898653], [52.373571, 4.898272]],
    columns=['lat', 'lon'])

locations_names = {'GAWW-11': 'Korte Niezel', 'GAWW-12': 'Oudekennissteeg', 'GAWW-14': 'Oudezijds Voorburgwal'}

all_forecasts = forecast1
all_forecasts = all_forecasts.rename(columns={'prediction': 'GAWW-11'})
all_forecasts['GAWW-12'] = forecast2.prediction
all_forecasts['GAWW-14'] = forecast3.prediction
all_forecasts['total'] = all_forecasts['GAWW-11'] + all_forecasts['GAWW-12'] + all_forecasts['GAWW-14']
all_forecasts['datetime2'] = pd.to_datetime(all_forecasts.datetime)
# all_forecasts['datetime2'] = all_forecasts.index

# Add the thresholds
for ind, loc in enumerate(locations):
    loc_info = sensors_info[sensors_info['objectnummer'] == 'CMSA-' + loc]
    all_forecasts[loc + '_th_low'] = loc_info['crowd_threshold_low'][ind]
    all_forecasts[loc + '_th_high'] = loc_info['crowd_threshold_high'][ind]


def get_weather(w1, w2, w3):
    try:
        # GET THE CURRENT WEATHER IN AMSTERDAM:
        r = re.get('http://api.weatherapi.com/v1/current.json?key=16a275e088724a3eba1143500221201&q=Amsterdam&aqi=no')
        weather = r.json()
        icon = "http:" + str(weather['current']['condition']['icon'])
        # st.write("Current temperature in Amsterdam:",weather['current']['temp_c'],"degrees Celsius")
        # st.markdown("![weather icon](" + icon + ")")
        w3.write(" ") # fix spacing
        w3.markdown("![weather icon](" + icon + ")")
        w1.metric("Temperature", str(weather['current']['temp_c']) + " °C")
        w2.metric("Wind", str(weather['current']['wind_kph']) + " kph")
    except:
        # In case there's no internet connection
        pass


def get_map():
    global day_pred
    global hour
    location1_df = pd.DataFrame([[52.374611, 4.899833]], columns=['lat', 'lon'])
    location2_df = pd.DataFrame([[52.373883, 4.898653]], columns=['lat', 'lon'])
    location3_df = pd.DataFrame([[52.373571, 4.898272]], columns=['lat', 'lon'])

    locations_text = pd.DataFrame([[52.374611, 4.899833 - 0.0009, 'Korte Niezel'],
                                   [52.373883, 4.898653 - 0.0011, 'Oudekennissteeg'],
                                   [52.373571, 4.898272 - 0.0014, 'Oudezijds Voorburgwal']],
                                  columns=['lat', 'lon', 'text'])
    loc_colors, crowds = get_colors(day_pred, hour)

    date = datetime.datetime.combine(day_pred, hour).strftime("%Y-%m-%d %H:%M:%S")
    crowds = all_forecasts[all_forecasts['datetime'] == date]

    if crowds.size > 0:
        crowds = crowds.iloc[0]
        locations_crowd = pd.DataFrame([[52.374611, 4.899833, str(int(crowds['GAWW-11']))],
                                        [52.373883, 4.898653, str(int(crowds['GAWW-12']))],
                                        [52.373571, 4.898272, str(int(crowds['GAWW-14']))]],
                                       columns=['lat', 'lon', 'text'])
    else:
        locations_crowd = pd.DataFrame([[52.374611 - 0.0001, 4.899833 - 0.0009, ''],
                                        [52.373883 - 0.0001, 4.898653 - 0.0011, ''],
                                        [52.373571 - 0.0001, 4.898272 - 0.0015, '']], columns=['lat', 'lon', 'text'])

    # st.write(gg[gg['datetime']==date])

    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=52.374,
            longitude=4.899,
            zoom=16,
            min_zoom=16,
            max_zoom=16,
            height=400,
            width='100%',
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-11'].replace(']', ',160]'),
                get_radius=15,
            ),
            pdk.Layer(
                "TextLayer",
                pickable=True,
                data=locations_text,
                get_position='[lon, lat]',
                get_text="text",
                get_size=25,
                get_color=[0, 0, 0],
                get_angle=0,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-12'].replace(']', ',160]'),
                get_radius=15,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-14'].replace(']', ',160]'),
                get_radius=15,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location1_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-11'],
                get_radius=5,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location2_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-12'],
                get_radius=5,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=location3_df,
                get_position='[lon, lat]',
                get_color=loc_colors['GAWW-14'],
                get_radius=5,
            ),
            pdk.Layer(
                "TextLayer",
                pickable=True,
                data=locations_crowd,
                get_position='[lon, lat]',
                get_text="text",
                get_size=30,
                get_color=[0, 0, 0],
                get_angle=0,
            ),
        ],
    )

    return map


def get_crowd():
    crowds = {}
    crowds_combined = {}
    for ind, loc in enumerate(locations):
        loc_info = sensors_info[sensors_info['objectnummer'] == 'CMSA-' + loc]
        loc_forecast = pd.read_csv('experiments/fake_forecasts_for_frontend/' + loc + '.csv')

        # Get the times with yellow forecast:
        yellow_forecast = loc_forecast[loc_forecast['prediction'] > loc_info['crowd_threshold_low'][ind]]
        if yellow_forecast.shape[0] > 0:
            yellow_forecast = yellow_forecast[yellow_forecast['prediction'] < loc_info['crowd_threshold_high'][ind]]

        # Get the times with red forecast:
        red_forecast = loc_forecast[loc_forecast['prediction'] > loc_info['crowd_threshold_high'][ind]]

        crowds[loc] = {'yellow': yellow_forecast, 'red': red_forecast}

        # MERGE OVERCROWDED FORECASTS:
        yellow = yellow_forecast
        yellow['overcrowdedness'] = 'orange'
        yellow.set_index('datetime')

        red = red_forecast
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
            elif not (cut_row.get('overcrowdedness') == row.overcrowdedness):
                rowlist.append(cut_row)
                cut_row = row._asdict()
            elif (row.start - cut_row.get('end')) < datetime.timedelta(minutes=16):
                cut_row['end'] = row.end
            else:
                rowlist.append(cut_row)
                cut_row = row._asdict()
        rowlist.append(cut_row)
        combine_merged = pd.DataFrame.from_dict(rowlist)

        crowds_combined[loc] = combine_merged

    return crowds, crowds_combined


def get_crowded_moments():
    crowds, crowds_combined = get_crowd()
    for loc in crowds:
        st.subheader(locations_names[loc])

        if 'Index' in crowds_combined[loc].columns:
            combined = crowds_combined[loc].drop(['Index', 'datetime', 'prediction'], axis=1)
            combined = crowds_combined[loc]
            combined['date'] = combined.start.dt.date
            combined['start_time'] = combined.start.dt.time
            combined['end_time'] = combined.end.dt.time

            text_info = []
            for date in combined.date.unique():
                # st.write(date.strftime("%d-%m-%Y"))
                text_info.append(f'<b> {date.strftime("%A %d %b %-y")} </b>')
                dff = combined[combined['date'] == date]
                for row in dff.itertuples():
                    if row.start_time == row.end_time:
                        end = row.end + datetime.timedelta(minutes=15)
                        end = end.time()
                    else:
                        end = row.end_time
                    if row.overcrowdedness == 'red':
                        text_info.append(f' 🔴  {row.start_time.strftime("%H:%M")} - {end.strftime("%H:%M")}')
                    if row.overcrowdedness == 'orange':
                        text_info.append(f' 🟡  {row.start_time.strftime("%H:%M")} - {end.strftime("%H:%M")}')
                text_info.append("")

            st.write("<br>".join(text_info), unsafe_allow_html=True)

        else:
            st.write('No overcrowded moments for this location in the next 7 days')


def get_colors(day_pred, hour):
    red = '[255,0,0]'
    yellow = '[252,211,57]'
    green = '[0,150,50]'

    crowds, crowds_df = get_crowd()
    date = datetime.datetime.combine(day_pred, hour)
    loc_colors = {}

    for ind, loc in enumerate(locations):
        if str(date) in crowds[loc]['red'].datetime.tolist():
            loc_colors[loc] = red
        elif str(date) in crowds[loc]['yellow'].datetime.tolist():
            loc_colors[loc] = yellow
        else:
            loc_colors[loc] = green
    return loc_colors, crowds_df


def get_plot_prediction():
    horizon = st.select_slider('Prediction horizon:',
                               options=['1 day', '2 days', '3 days', '4 days', '5 days', '6 days', '7 days'],
                               value='3 days')
    options_loc = st.multiselect('Select locations',
                                 [locations_names["GAWW-11"], locations_names["GAWW-12"], locations_names["GAWW-14"]],
                                 [locations_names["GAWW-11"], locations_names["GAWW-12"], locations_names["GAWW-14"]])

    colors_list = ['#D31222', '#69292E', '#445769']
    colors_dict = {'GAWW-11': '#D31222', 'GAWW-12': '#69292E', 'GAWW-14': '#445769'}

    end_plot = first_forecast + datetime.timedelta(days=int(horizon.split(' da')[0]))

    global all_forecasts
    forecasts = all_forecasts[all_forecasts['datetime2'] < end_plot]

    fig = go.Figure()
    # loc_radio = st.radio("Location", ("All", "GAWW-11", "GAWW-12", "GAWW-14"))

    locations_names_2 = {v: k for k, v in locations_names.items()}

    if len(options_loc) > 0:
        for ind, loc2 in enumerate(options_loc):
            loc = locations_names_2[loc2]
            fig.add_trace(
                go.Scatter(
                    x=forecasts.datetime2,
                    y=forecasts[loc],
                    text=loc2,
                    name=loc2,
                    line_color=colors_dict[loc],
                    line_width=2))
            if len(options_loc) == 1:
                fig.add_trace(
                    go.Scatter(
                        x=forecasts.datetime2,
                        y=forecasts[loc + '_th_high'],
                        line_color=colors_dict[loc],
                        text='High threshold',
                        name='High threshold',
                        line_width=0.5)
                )
                fig.add_trace(
                    go.Scatter(
                        x=forecasts.datetime2,
                        y=forecasts[loc + '_th_low'],
                        line_color='#808080',
                        text='Low threshold',
                        name='Low threshold',
                        line_width=0.5)
                )
            fig.update_xaxes(tickformat="%H:%M\n%a %-d %b '%-y")
    else:
        pass

    fig.update_layout(
        # title="7 Day prediction",
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

    st.plotly_chart(fig, use_container_width=True)


def get_map_prediction():
    global day_pred
    global hour

    # st.map(locations_df, zoom=14.5)
    map = get_map()
    st.pydeck_chart(map)

    st.write("Prediction for day: ", day_pred.date(), ", at: ", hour)
    day_pred = st.slider('Prediction day:', value=first_forecast,
                         min_value=first_forecast,
                         max_value=last_forecast,
                         step=datetime.timedelta(days=1),
                         format='ddd D MMM')
    hour = st.slider('Hour of the day:', value=datetime.time(12, 00, 00),
                     min_value=datetime.time(00, 00, 00),
                     max_value=datetime.time(23, 45, 00),
                     step=datetime.timedelta(minutes=15),
                     format='H:mm')


def convert_date(row):
    gg = datetime.datetime.strptime(row['datetime2'], '%Y-%m-%d %H:%M:%S')
    return gg
