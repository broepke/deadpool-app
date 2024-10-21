"""
Simple display of all picks
"""
import streamlit as st
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper


st.set_page_config(page_title="All Draft Picks", page_icon=":skull:")

st.title("Draft Picks :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-draft-picks")
    authenticator.login(location="unrendered", key="deadpool-app-login-draft-picks")
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")


    # Initialize connection.
    conn = snowflake_connection_helper()

    df_2024 = load_snowflake_table(conn, "picks_twenty_four")
    df_2023 = load_snowflake_table(conn, "picks_twenty_three")

    st.header("2024 Draft Picks:")
    st.dataframe(df_2024)

    st.subheader("2024 Draft Picks by Person")

    df_picks = load_snowflake_table(conn, "draft")
    df_picks.drop(columns="ID", inplace=True)
    st.dataframe(df_picks, use_container_width=True)

    st.header("2023 Draft Picks:")
    st.dataframe(df_2023, use_container_width=True)

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()