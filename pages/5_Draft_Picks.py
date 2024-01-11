"""
Simple display of all picks
"""
import streamlit as st
from utilities import check_password, load_snowflake_table, run_snowflake_query

st.set_page_config(page_title="All Draft Picks", page_icon=":skull:")

email, user_name, authticated = check_password()
if authticated:
    # Initialize connection.
    conn = st.connection("snowflake")

    df_2024 = load_snowflake_table(conn, "picks_twenty_four")
    df_2023 = load_snowflake_table(conn, "picks_twenty_three")

    st.title("2024 Draft Picks:")
    st.dataframe(df_2024)

    st.title("2024 Draft Picks by Person")

    query = """
    select 
    concat(first_name || ' ' || last_name) as name, 
    count(*) as total_picks
    from deadpool.prod.picks pi
    join deadpool.prod.players pl
    on pi.picked_by = pl.id
    where year = 2024
    group by 1;
    """

    df_pics_by_player = run_snowflake_query(conn, query)
    st.dataframe(df_pics_by_player)

    st.header("2023 Draft Picks:")
    st.dataframe(df_2023)
