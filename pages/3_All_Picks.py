"""
Simple display of all picks
"""
import streamlit as st
from Home import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


# Initialize connection.
conn = st.connection("snowflake")


def load_picks_table(table):
    session_picks = conn.session()
    return session_picks.table(table).to_pandas()


df_picks = load_picks_table("picks")

df_2024 = df_picks[df_picks['YEAR'] == 2024]
df_2023 = df_picks[df_picks['YEAR'] == 2023]

st.title("2024 Draft Picks:")
st.dataframe(df_2024)

st.header("2023 Draft Picks:")
st.dataframe(df_2023)
