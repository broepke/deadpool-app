"""
Simple display of all picks
"""
import streamlit as st


# Initialize connection.
conn = st.connection("snowflake")


@st.cache_data
def load_picks_table():
    session_picks = conn.session()
    return session_picks.table("picks").to_pandas()


df_picks = load_picks_table()

st.title("All Draft Picks:")
st.dataframe(df_picks)
