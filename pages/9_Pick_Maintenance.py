"""
Tools to modify pick information mostly the wiki page
"""

import streamlit as st
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper

st.set_page_config(page_title="Draft Pick Maintenance", page_icon=":skull:")

st.title("Draft Pick Maintenance :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-pick-maintenance")
    authenticator.login(
        location="unrendered", key="deadpool-app-login-pick-maintenance"
    )
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    st.markdown(
        """
    Use this form to fix the Wikipedia links if they were not guessed properly by the code when loaded.  In some cases there are disambiguation data such as '(actor)' for common names or there can be other URL encoding for special characters in names.
    1. Select a name.
    2. Update the Wiki link only using the end of the URL such as '**Tina_Turner**' in https://en.wikipedia.org/wiki/Tina_Turner.
    3. Submit your adjustments.
    """  # noqa: E501
    )

    # Initialize important varibles
    SEL_NAME = ""
    SEL_WIKI_PAGE = ""

    # Initialize connection.
    conn = snowflake_connection_helper()

    df_picks = load_snowflake_table(conn, "people")

    df_picks_list = df_picks["NAME"].to_list()
    df_picks_list.sort()

    st.header("Pick Selection")

    # Load all the picks into a drop down for easy selection
    with st.form("Pick to Update"):
        sel_pick = st.selectbox("Select a pick", df_picks_list, key="sel_selected_pick")  # noqa: E501

        submitted = st.form_submit_button("Choose pick")

        if submitted:
            filtered_df = df_picks[df_picks["NAME"] == sel_pick]

            if not filtered_df.empty:
                SEL_ID = filtered_df.iloc[0]["ID"]
                SEL_NAME = filtered_df.iloc[0]["NAME"]
                SEL_WIKI_PAGE = filtered_df.iloc[0]["WIKI_PAGE"]
                SEL_WIKI_ID = filtered_df.iloc[0]["WIKI_ID"]

                st.session_state["reg_id"] = SEL_ID
                st.session_state["reg_name"] = SEL_NAME
                st.session_state["reg_wiki_page"] = SEL_WIKI_PAGE
                st.session_state["reg_wiki_id"] = SEL_WIKI_ID

            else:
                print("No user found with the given email")

    st.header("Update Pick Information")

    with st.form("Pick Data"):
        try:
            SEL_ID = st.session_state["reg_id"]
            SEL_NAME = st.session_state["reg_name"]
            SEL_WIKI_PAGE = st.session_state["reg_wiki_page"]
            SEL_WIKI_ID = st.session_state["reg_wiki_id"]
        except KeyError:
            SEL_ID = ""
            SEL_NAME = ""
            SEL_WIKI_PAGE = ""
            SEL_WIKI_ID = ""

        sub_name = st.text_input(
            "First Name:",
            SEL_NAME,
            256,
            key="_reg_name",
        )
        sub_wiki_page = st.text_input(
            "Wiki Page:", SEL_WIKI_PAGE, 256, key="_reg_wiki_page"
        )
        sub_wiki_id = st.text_input("Wiki ID:", SEL_WIKI_ID, key="_reg_wiki_id")  # noqa: E501

        submitted = st.form_submit_button("Submit")
        if submitted:
            WRITE_QUERY = """UPDATE people SET name = %s, wiki_page = %s, wiki_id = %s WHERE id = %s """

            # Execute the query with parameters
            conn.cursor().execute(
                WRITE_QUERY, (sub_name, sub_wiki_page, sub_wiki_id, SEL_ID)
            )

            # Display the query and parameters in Streamlit
            st.caption(f"Query: {WRITE_QUERY}")
            st.caption(f"ID: {SEL_ID}")
            st.caption(f"New Name: {sub_name}")
            st.caption(f"New Wiki Page: {sub_wiki_page}")
            st.caption(f"New Wiki ID: {sub_wiki_id}")
            st.caption(f"Original Name: {SEL_NAME}")

            # Clear out the form fields
            SEL_ID = ""
            SEL_NAME = ""
            SEL_WIKI_PAGE = ""
            SEL_WIKI_ID = ""

            st.session_state["reg_id"] = ""
            st.session_state["reg_name"] = ""
            st.session_state["reg_wiki_page"] = ""
            st.session_state["reg_wiki_id"] = ""

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()
