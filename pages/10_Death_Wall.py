import streamlit as st
from dp_utilities import check_password

st.set_page_config(page_title="Death Wall", page_icon=":skull:")

st.title("Death Wall :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Joyce Randolph")
        st.write("Joyce Randolph (October 21, 1924 - January 13, 2024) was an American actress of stage and television, best known for playing Trixie Norton on The Jackie Gleason Show and the television sitcom The Honeymooners.")  # noqa: E501
        st.image("https://upload.wikimedia.org/wikipedia/commons/0/0e/Joyce_Randolph_1963_%28cropped%29.JPG")  # noqa: E501

    with col2:
        st.subheader("TBD")
        st.write("Comming soon... ")
