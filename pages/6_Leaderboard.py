"""
Display leaderboards and other stats for the games
"""

import streamlit as st
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper

st.set_page_config(page_title="Leaderboard", page_icon=":skull:")

st.title("Leaderboards :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-leaderboard")
    authenticator.login(location="unrendered", key="deadpool-app-login-leaderboard")
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    # Initialize connection.
    conn = snowflake_connection_helper()

    df_score_current = load_snowflake_table(conn, "score_current_year")
    df_score_2024 = load_snowflake_table(conn, "score_twenty_four")
    df_score_2023 = load_snowflake_table(conn, "score_twenty_three")

    df_score_current.drop(columns=["EMAIL", "ID"], inplace=True)
    df_score_2024.drop(columns=["EMAIL", "ID"], inplace=True)
    df_score_2023.drop(columns=["EMAIL", "ID"], inplace=True)

    st.header("Current Leaderboard:")

    st.dataframe(
        df_score_current.style.highlight_max(axis=0, subset=["TOTAL"]),
        use_container_width=True,
    )

    st.bar_chart(data=df_score_current, x="PLAYER", y="TOTAL", color="#F63366")

    st.header("2024 Results")

    st.dataframe(
        df_score_2024.style.highlight_max(axis=0, subset=["TOTAL"]),
        use_container_width=True,
    )

    st.bar_chart(data=df_score_2024, x="PLAYER", y="TOTAL", color="#F63366")

    st.header("2023 Results")

    st.dataframe(
        df_score_2023.style.highlight_max(axis=0, subset=["TOTAL"]),
        use_container_width=True,
    )

    st.bar_chart(data=df_score_2023, x="PLAYER", y="TOTAL", color="#F63366")

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()
