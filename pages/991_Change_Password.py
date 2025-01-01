import streamlit as st
import yaml
from dp_utilities import mp_track_page_view

PAGE_TITLE = "Change Password"
PAGE_ICON = ":skull:"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

st.title("Reset Password :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-change-password")
    authenticator.login(location="unrendered", key="deadpool-app-login-change-password")
    
    mp_track_page_view(PAGE_TITLE)
    
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success("Password modified successfully")

            config = st.session_state.config

            with open("config.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False)

    except Exception as e:
        st.error(e)
else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()
