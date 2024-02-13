import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

authenticator.login("Login", "main")


if st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")

elif st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar", key="unique_key")
    name = st.session_state["name"]
    email = st.session_state["username"]

    st.title("Some content")

    st.sidebar.write(f"Welcome, {name}")
