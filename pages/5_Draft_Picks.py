"""
Simple display of all picks
"""
import streamlit as st
from dp_utilities import check_password
from dp_utilities import load_snowflake_table
from dp_utilities import run_snowflake_query

st.set_page_config(page_title="All Draft Picks", page_icon=":skull:")

st.title("Draft Picks :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
    # Initialize connection.
    conn = st.connection("snowflake")

    df_2024 = load_snowflake_table(conn, "picks_twenty_four")
    df_2023 = load_snowflake_table(conn, "picks_twenty_three")

    st.header("2024 Draft Picks:")
    st.dataframe(df_2024)

    st.subheader("2024 Draft Picks by Person")

    query = """
    SELECT
    CONCAT(FIRST_NAME || ' ' || LAST_NAME) AS NAME,
    YEAR_TWO,
    COUNT(*) AS TOTAL_PICKS
    FROM DEADPOOL.PROD.PICKS PI
    JOIN DEADPOOL.PROD.PLAYERS PL
    ON PI.PICKED_BY = PL.ID
    WHERE YEAR = 2024
    AND PI.DEATH_DATE IS NULL
    GROUP BY 1, 2
    ORDER BY 2
    """

    df_pics_by_player = run_snowflake_query(conn, query)
    st.dataframe(df_pics_by_player, use_container_width=True)

    st.header("2023 Draft Picks:")
    st.dataframe(df_2023, use_container_width=True)
