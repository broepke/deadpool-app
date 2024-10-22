import streamlit as st
import yaml

st.set_page_config(page_title="Reset Password", page_icon=":skull:")

st.title("Reset Password :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-user-profile")
    authenticator.login(location="unrendered", key="deadpool-app-login-user-profile")
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    try:
        if authenticator.update_user_details(st.session_state["username"]):
            st.success("Entries updated successfully")
            config = st.session_state.config

            with open("config.yaml", "w") as file:
                yaml.dump(config, file, default_flow_style=False)

    except Exception as e:
        st.error(e)

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()

# Check for Admin Access
try:
    user_roles = st.session_state["config"]["credentials"]["usernames"][st.session_state.username].get("roles")

    if "admin" in user_roles:
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