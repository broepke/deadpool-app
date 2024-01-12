import streamlit as st
from dp_utilities import check_password

st.set_page_config(page_title="Death Wall", page_icon=":skull:")

email, user_name, authticated = check_password()
if authticated:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Rosalin Carter")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Rose_Carter%2C_official_color_photo%2C_1977-cropped.jpg/440px-Rose_Carter%2C_official_color_photo%2C_1977-cropped.jpg")

    with col2:
        st.header("Henry Kissinger")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Henry_A._Kissinger%2C_U.S._Secretary_of_State%2C_1973-1977.jpg/440px-Henry_A._Kissinger%2C_U.S._Secretary_of_State%2C_1973-1977.jpg")

    with col3:
        st.header("Bob Barker")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Bob_Barker_1975.jpg/440px-Bob_Barker_1975.jpg")
