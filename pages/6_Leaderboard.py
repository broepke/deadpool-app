"""
Display leaderboards and other stats for the games
"""
import streamlit as st
from dp_utilities import check_password
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper

st.set_page_config(page_title="Leaderboard", page_icon=":skull:")

st.title("Leaderboards :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
    # Initialize connection.
    conn = snowflake_connection_helper()

    df_score_2024 = load_snowflake_table(conn, "SCORE_TWENTY_FOUR")
    df_score_2023 = load_snowflake_table(conn, "SCORE_TWENTY_THREE")

    df_score_2024.drop(columns="EMAIL", inplace=True)
    df_score_2023.drop(columns="EMAIL", inplace=True)

    st.header("2024 Leaderboard:")

    st.dataframe(
        df_score_2024.style.highlight_max(axis=0, subset=["SCORE"]),
        use_container_width=True,
    )

    st.bar_chart(data=df_score_2024, x="PLAYER", y="SCORE", color="#F28749")

    st.header("2023 Leaderboard:")

    st.dataframe(
        df_score_2023.style.highlight_max(axis=0, subset=["SCORE"]),
        use_container_width=True,
    )

    st.bar_chart(data=df_score_2023, x="PLAYER", y="SCORE", color="#F28749")
