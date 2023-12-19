"""
Simple display of all picks
"""
import streamlit as st
from utilities import check_password, get_user_name, load_snowflake_table

st.set_page_config(page_title="All Draft Picks", page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except:
    st.write("Please login again")

# Initialize connection.
conn = st.connection("snowflake")


df_picks = load_snowflake_table(conn, "picks")

df_2024 = df_picks[df_picks["YEAR"] == 2024]
df_2023 = df_picks[df_picks["YEAR"] == 2023]

st.title("2024 Draft Picks:")
st.dataframe(df_2024)

st.header("2023 Draft Picks:")
st.dataframe(df_2023)
