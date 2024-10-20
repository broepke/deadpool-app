import streamlit as st
import yaml
from dp_utilities import check_password

st.set_page_config(page_title="Reset Password", page_icon=":skull:")

st.title("Reset Password :skull_and_crossbones:")

email, user_name, authenticator, config, authenticated = check_password()
if authenticated:
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success("Password modified successfully")
    except Exception as e:
        st.error(e)

with open("config.yaml", "w") as file:
    yaml.dump(config, file, default_flow_style=False)
