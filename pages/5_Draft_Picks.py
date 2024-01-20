"""
Simple display of all picks
"""
import streamlit as st
from dp_utilities import check_password
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper


st.set_page_config(page_title="All Draft Picks", page_icon=":skull:")

st.title("Draft Picks :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
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
