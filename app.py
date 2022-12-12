from multipage import MultiPage
from pages import home, hub, datapage, about
import streamlit as st
from PIL import Image


favicon = Image.open('pages/elements/favicon.png')

# SET DEFAULT PAGE CONFIGS
st.set_page_config(
     page_title="PLACE - Crowdedness information hub",
     page_icon=favicon,
     layout="wide",
 )


# Create an instance of the app 
app = MultiPage()

# Title of the main page
st.title('PLACE crowdedness centre')
# Add all your application here
app.add_page("Home", home.app)
app.add_page("Info hub", hub.app)
app.add_page("Data", datapage.app)
app.add_page("About",about.app)

# The main app
app.run()