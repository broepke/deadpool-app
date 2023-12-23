"""
Simple display of all picks
"""
import streamlit as st
from utilities import check_password, get_user_name, load_snowflake_table

st.set_page_config(page_title="All Draft Picks",
                   page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except KeyError:
    st.write("Please login again")

# Initialize connection.
conn = st.connection("snowflake")


df_2024 = load_snowflake_table(conn, "picks_twenty_four")
df_2023 = load_snowflake_table(conn, "picks_twenty_three")

st.title("2024 Draft Picks:")
st.dataframe(df_2024)

st.header("2023 Draft Picks:")
st.dataframe(df_2023)
