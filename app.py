import streamlit as st
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from st_aggrid import AgGrid

# SET DEFAULT PAGE CONFIGS
st.set_page_config(
    page_title="Overcrowding detection tool",
    page_icon="🛴",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Crowd count prediction and overcrowding detection")
st.markdown(
    "This tool is developing bitch"
)

start_date = st.sidebar.date_input("Start date", datetime.date.today())
end_date = st.sidebar.date_input("End date", datetime.date.today())
sensor = st.sidebar.text_input("Sensor location", "Kloveniersburgwal")
granularity= st.sidebar.st.sidebar.selectbox("Granularity", ("15 mins", "30 mins", "hour"))

# Prepare the data
sensor1 = pd.read_csv("result/CMSA-GAWW-22_forecast.csv", index_col="Unnamed: 0")
start_date = "10/10/2021"
end_date = "11/10/2021"

# Block 1: Map view

# Block 2: Overcrowd moment
st.markdown("### Overcrowding moments")
st.markdown("Time between {} and {} where overcrowding is expected to happen. Actions should be taken!".format(start_date, end_date))

# Prepare the data
threshold = 182.5 # fake shit
overcrowd = sensor1[sensor1.forecast > threshold][["objectnummer", "location", "datetime", "forecast", "threshold"]][:10]
overcrowd["forecast"] = overcrowd["forecast"].round()
overcrowd["warning_level"] = "high"

AgGrid(
    overcrowd,
    height=200,
    filter=True,
    fit_columns_on_grid_load=True,
    wrap_text=True
    )

# Block 3: Prediction plot
st.markdown("### Predicted crowd count every 15 minutes")
# Prepare the data
location = sensor1.iloc[0, 1]

# Make the line plot with confidence interval
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=sensor1['datetime'], 
        y=sensor1['forecast'],
        mode="lines+markers", 
        name="Predicted crowd"),
        )
fig.add_trace(
    go.Scatter(
        x=sensor1['datetime'], 
        y=sensor1['upper_bound'], 
        name="Upper bound"))
fig.add_trace(
    go.Scatter(
        x=sensor1['datetime'], 
        y=sensor1['lower_bound'], 
        name="Lower bound", 
        fill="tonexty"))
fig.add_trace(
    go.Scatter(
        x=sensor1['datetime'], 
        y=sensor1['threshold'], 
        name="Threshold"))

fig.update_layout(
    title="Predicted number of pedestrian at {} every 15 minute from {} to {}".format(location,start_date, end_date),
    autosize=False,
    width=900,
    height=350,
    showlegend=True,
    margin=dict(l=40, r=40, b=40, t=60),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=0.96)
)

fig.update_traces()
fig.update_xaxes(tickangle=-45, nticks=int(round(len(sensor1)/2)))

st.plotly_chart(fig)

st.markdown("##### It should look like this at some point")
st.image("img/example1.png", width=900)

# Block 4: Heatmap
st.markdown("### Predicted average crowd each location every hour between {} and {}".format(start_date, end_date))

# Prepare the data
sensor1["hour"] = sensor1.datetime.astype('datetime64[h]')
avg_crowd_per_hour = pd.pivot_table(sensor1, values="forecast", index="hour", columns="location", aggfunc=np.mean)

# Heatmap
cm = sns.light_palette("green", as_cmap=True)
st.dataframe(avg_crowd_per_hour.style.background_gradient(cmap=cm).format(precision=1), width=1000, height=400)

st.markdown("Another idea:")
st.image("img/example2.png", width=900)