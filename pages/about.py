import streamlit as st
def app():
    st.header('About the project')
    st.markdown('PLACE was built as part of the MSc Information Studies: Data Science\
         at the University of Amsterdam. This was a joint project between \
         the UvA and the City of Amsterdam. The aim of the project is to create a proof-of-concept\
        of an application that incorporates the Citys ambition to use data-driven solutions to \
        increase the citys livability. PLACE does this by mimicking the City of Amsterdams \
        existing prediction model for crowdedness based on CMSA passenger data and improving it.' )

    st.header('About the team')

    w2, w3, w4, w5, w6 = st.columns(5)

    w4.image("memoji/chieling.png")
    w4.markdown("<h3 style='text-align: center;'>Chieling Yue</h3>", unsafe_allow_html=True)
    w4.markdown("<p style='text-align: center;'>chielingyueh@gmail.com</p>", unsafe_allow_html=True)

    w5.image("memoji/emiel.png")
    w5.markdown("<h3 style='text-align: center;'>Emiel Steegh</h3>", unsafe_allow_html=True)
    w5.markdown("<p style='text-align: center;'>emielSteegh@gmail.com</p>", unsafe_allow_html=True)

    w6.image("memoji/paula.png")
    w6.markdown("<h3 style='text-align: center;'>Paula Sorolla</h3>", unsafe_allow_html=True)
    w6.markdown("<p style='text-align: center;'>paula.sorolla@gmail.com</p>", unsafe_allow_html=True)

    w3.image("memoji/aiden.png")
    w3.markdown("<h3 style='text-align: center;'>Aiden Ta</h3>", unsafe_allow_html=True)
    w3.markdown("<p style='text-align: center;'>taanh1999GHA@gmail.com</p>", unsafe_allow_html=True)

    w2.image("memoji/laura.png")
    w2.markdown("<h3 style='text-align: center;'>Laura Hilhorst</h3>", unsafe_allow_html=True)
    w2.markdown("<p style='text-align: center;'>laura.hilhorst2@gmail.com</p>", unsafe_allow_html=True)



