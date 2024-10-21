"""
List of all scoring rules
"""
import streamlit as st
import requests
from dp_utilities import check_password

st.set_page_config(page_title="GitHub Updater Status", page_icon=":skull:")

st.title("GitHub Updater Status :skull_and_crossbones:")

email, user_name, authenticator, config, authenticated = check_password()
if authenticated:

    def check_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.success("The GitHub Updater service is running")
            else:
                st.warning("WARNING: the sevice returns a {response.status_code} status code")
        except requests.exceptions.RequestException as e:
            st.error(f"Error checking {url}: {e}")

    check_url("https://deadpool.dataknowsall.com:5000/health_check")
    