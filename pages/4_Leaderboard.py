import streamlit as st
from Deadpool import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


# Initialize connection.
conn = st.connection("snowflake")


@st.cache_data
def load_score_table(table):
    session_score = conn.session()
    return session_score.table(table).to_pandas()


df_score_2024 = load_score_table("score_two")
df_score_2023 = load_score_table("score_one")


st.title("2024 Leaderboard:")

st.dataframe(
    df_score_2024.style.highlight_max(axis=0, subset=["SCORE"]),
    use_container_width=True,
)

st.bar_chart(data=df_score_2024, x="PLAYER", y="SCORE")

st.header("2023 Leaderboard:")

st.dataframe(
    df_score_2023.style.highlight_max(axis=0, subset=["SCORE"]),
    use_container_width=True,
)

st.bar_chart(data=df_score_2023, x="PLAYER", y="SCORE")
