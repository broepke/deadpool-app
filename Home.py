"""
Streamlit main app
"""

import time
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="Deadpool", page_icon=":skull:")
st.title("Deadpool 2024 :skull_and_crossbones:")

# Get all credentials
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    auto_hash=True,
)

# Store the authenticator and config in the session state
# This will be used across the other pages to persist login.
# The config is written to the config.yaml file when changes are made
st.session_state["authenticator"] = authenticator
st.session_state["config"] = config

# --- Authentication Code
try:
    authenticator.login(location="main", key="deadpool-app-login-home")
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    authenticator.logout(location="sidebar", key="deadpool-app-logout-home")
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    try:
        start_time = time.time()
        # output = the_arbiter(prompt, arbiter_version="base")
        output = "Greetings, savages. All judgements are final."

        # Calculate the time taken and print it
        end_time = time.time()
        time_taken = end_time - start_time
        st.markdown("**A message from The Arbiter:** " + output)

    except Exception as e:
        st.write(e)
        st.write("Welcome Back, " + user_name)

    st.image("arbiter.jpg", "The Arbiter")


elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")


# Check for Admin Access
try:
    user_roles = st.session_state["config"]["credentials"]["usernames"][st.session_state.username].get("roles")

    if "admin" in user_roles:
        st.subheader("Admin Tools")
        # Download button for updated config.yaml
        def download_config():
            config_data = yaml.dump(st.session_state["config"])
            st.download_button(
                label="Download Updated Config",
                data=config_data,
                file_name="config.yaml",
                mime="text/yaml",
            )

        download_config()

        # Session State for Debugging
        with st.expander("Session State for Debugging", icon="💾"):
            st.session_state

except KeyError:
    pass
