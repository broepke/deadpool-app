"""
List of all scoring rules
"""

import streamlit as st

from dp_utilities import load_snowflake_table, snowflake_connection_helper

st.set_page_config(page_title="Draft Order", page_icon=":skull:")

st.title("Draft Order :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-draft-order")
    authenticator.login(location="unrendered", key="deadpool-app-login-draft-order")
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    conn = snowflake_connection_helper()

    df_ord = load_snowflake_table(conn, "players")

    df_sorted = df_ord.sort_values(by="YEAR_TWO").reset_index(drop=True)

    df_sorted.drop(
        columns=["EMAIL", "YEAR_ONE", "OPT_IN", "SMS", "ID"], inplace=True
    )

    st.subheader("2024 Draft Order")

    st.markdown(
        """

    **Draft Order**:
    - Draft order has been computed to weigh the prior year's draft order and the number of points scored by the player.  The high draft order and higher scores penalized your spot in the new order.
    - Additionally, a random number has been applied for those who came later, which helps shuffle users who didn't play a little last year.
    - All numbers are normalized between 0 and 1.
    - Finally the calculation is: `ORDER + RANDOM + (SCORE * -1)`.
    """  # noqa: E501
    )

    st.dataframe(df_sorted, use_container_width=True)

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()
