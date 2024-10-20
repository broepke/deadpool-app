import streamlit as st
import yaml
from dp_utilities import check_password

st.set_page_config(page_title="Forgot Password", page_icon=":skull:")

st.title("Forgot Password :skull_and_crossbones:")

email, user_name, authenticator, config, authenticated = check_password()

# Forgot password
try:
    username_of_forgotten_password, email_of_forgotten_password, new_random_password = (
        authenticator.forgot_password()
    )
    if username_of_forgotten_password:
        st.success("New password to be sent securely")
        # st.code("Password: " + new_random_password)
    elif username_of_forgotten_password is False:
        st.error("Username not found")
except Exception as e:
    st.error(e)

# with open("config.yaml", "w") as file:
#     yaml.dump(config, file, default_flow_style=False)
