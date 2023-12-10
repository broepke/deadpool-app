import streamlit as st


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
