import streamlit as st
from home import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


# Initialize connection.
conn = st.connection("snowflake")


@st.cache_data
def load_score_table():
    session_score = conn.session()
    return session_score.table("score").to_pandas()


df_score = load_score_table()


st.title("Leaderboard")

st.dataframe(
    df_score.style.highlight_max(axis=0, subset=["SCORE"]), use_container_width=True
)

st.bar_chart(data=df_score, x="PLAYER", y="SCORE")
