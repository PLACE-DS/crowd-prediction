import streamlit as st
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from st_aggrid import AgGrid

from data_loading import crowd_sample

st.title("Crowd count prediction and overcrowding detection")
st.markdown(
    "This tool is developing bitch"
)

# AgGrid(crowd_sample)

start_date = st.sidebar.date_input("Start date", datetime.date.today())
end_date = st.sidebar.date_input("End date", datetime.date.today())
sensor = st.sidebar.text_input("Sensor location", "Kloveniersburgwal")

crowd_plot = st.expander('Actual crowd plot')

with crowd_plot:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=crowd_sample['Time'], y=crowd_sample['CMSA-GAWW-22 Kloveniersburgwal'], name="Kloveniersburgwal"))
    fig.add_trace(go.Scatter(x=crowd_sample['Time'], y=crowd_sample['CMSA-GAWW-23 Bloedstraat'], name="Bloedstraat"))
    fig.layout.update(title_text='Crowd count', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)