import streamlit as st
import requests as re 
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

st.set_page_config(layout="wide")


def app():
    st.title('Homepage')
    column1, column2 = st.columns(2)
 
    with column1:
        st.header("Prediction plot")
        forecast1 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-11.csv')
        forecast2 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-12.csv')
        forecast3 = pd.read_csv('experiments/fake_forecasts_for_frontend/GAWW-14.csv')
        st.write(forecast1.head())
        st.write(forecast2.head())
        st.write(forecast3.head())

    with column2:
        st.header("Realtime information")

r = re.get('http://api.weatherapi.com/v1/current.json?key=16a275e088724a3eba1143500221201&q=Amsterdam&aqi=no')

json = r.json()
icon = "http:" + str(json['current']['condition']['icon'])
st.write("Current temperature in Amsterdam:",json['current']['temp_c'],"degrees Celsius")
st.markdown("![weather icon](" + icon + ")")





