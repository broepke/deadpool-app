import streamlit as st
from Deadpool import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
except:
    st.write("Please login again")

if email != "broepke@gmail.com":
    st. write("Not authorized")
else:
    st.header("Maintenance Tools")

    # Initialize connection.
    conn = st.connection("snowflake")


    @st.cache_data
    def load_picks_table():
        session_picks = conn.session()
        return session_picks.table("players").to_pandas()


    df_players = load_picks_table()


    st.header("Current Players:")
    st.dataframe(df_players)