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

def app():
    st.title('Homepage')

r = re.get('http://api.weatherapi.com/v1/current.json?key=16a275e088724a3eba1143500221201&q=Amsterdam&aqi=no')

json = r.json()
icon = "http:" + str(json['current']['condition']['icon'])
st.write("Current temperature in Amsterdam:",json['current']['temp_c'],"degrees Celsius")
st.markdown("![weather icon](" + icon + ")")


