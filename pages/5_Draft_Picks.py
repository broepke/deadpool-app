"""
Simple display of all picks
"""
import streamlit as st
from utilities import check_password, load_snowflake_table

st.set_page_config(page_title="All Draft Picks", page_icon=":skull:")

email, user_name, authticated = check_password()
if authticated:
    # Initialize connection.
    conn = st.connection("snowflake")

    df_2024 = load_snowflake_table(conn, "picks_twenty_four")
    df_2023 = load_snowflake_table(conn, "picks_twenty_three")

    st.title("2024 Draft Picks:")
    st.dataframe(df_2024)

    st.header("2023 Draft Picks:")
    st.dataframe(df_2023)
