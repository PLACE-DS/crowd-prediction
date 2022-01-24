from multipage import MultiPage
from pages import home, hub, datapage, about # import your pages here
import streamlit as st
from PIL import Image


img = Image.open('favicon_PLACE_3.png')

# SET DEFAULT PAGE CONFIGS
st.set_page_config(
     page_title="PLACE - Crowdedness information hub",
     page_icon=img,
     layout="wide",
 )


# Create an instance of the app 
app = MultiPage()

# Title of the main page
st.title('PLACE crowdedness information hub')
# Add all your application here
app.add_page("Home", home.app)
app.add_page("Insights", hub.app)
app.add_page("Data", datapage.app)
app.add_page("About",about.app)

# The main app
app.run()