from multipage import MultiPage
from pages import home, hub, datapage, about # import your pages here
import streamlit as st

# Create an instance of the app 
app = MultiPage()

# Title of the main page
st.title('PLACE crowdedness information hub')
# Add all your application here
app.add_page("Home", home.app)
app.add_page("Historical information", hub.app)
app.add_page("Data", datapage.app)
app.add_page("About",about.app)

# The main app
app.run()