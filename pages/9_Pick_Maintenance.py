"""
Tools to modify pick information mostly the wiki page
"""
import streamlit as st
from utilities import check_password, load_snowflake_table

st.set_page_config(page_title="Draft Pick Maintenance", page_icon=":skull:")

st.title("Draft Pick Maintenance :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
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
    conn = st.connection("snowflake")

    df_picks = load_snowflake_table(conn, "picks")

    df_picks_2024 = df_picks[df_picks["YEAR"] == 2024]

    df_picks_list = df_picks_2024["NAME"].to_list()
    df_picks_list.sort()

    st.header("Pick Selection")

    # Load all the picks into a drop down for easy selection
    with st.form("Pick to Update"):
        sel_pick = st.selectbox(
            "Select a pick", df_picks_list, key="sel_selected_pick"
        )  # noqa: E501

        submitted = st.form_submit_button("Choose pick")

        if submitted:
            filtered_df = df_picks_2024[df_picks_2024["NAME"] == sel_pick]

            if not filtered_df.empty:
                SEL_NAME = filtered_df.iloc[0]["NAME"]
                SEL_WIKI_PAGE = filtered_df.iloc[0]["WIKI_PAGE"]

                st.session_state["reg_name"] = SEL_NAME
                st.session_state["reg_wiki_page"] = SEL_WIKI_PAGE

            else:
                print("No user found with the given email")

    st.header("Update Pick Information")

    with st.form("Pick Data"):
        try:
            SEL_NAME = st.session_state["reg_name"]
            SEL_WIKI_PAGE = st.session_state["reg_wiki_page"]
        except KeyError:
            SEL_NAME = ""
            SEL_WIKI_PAGE = ""

        sub_name = st.text_input(
            "First Name:",
            SEL_NAME,
            256,
            key="_reg_name",
        )
        sub_wiki_page = st.text_input(
            "Wiki Page:", SEL_WIKI_PAGE, 256, key="_reg_wiki_page"
        )

        submitted = st.form_submit_button("Submit")
        if submitted:
            WRITE_QUERY = "UPDATE picks SET wiki_page = :1 WHERE name = :2 AND year = 2024"  # noqa: E501

            # Execute the query with parameters
            conn.cursor().execute(WRITE_QUERY, (sub_wiki_page, sub_name))

            st.write(WRITE_QUERY)
            st.write(sub_name)
            st.write(sub_wiki_page)

            # Clear out the form fields
            SEL_NAME = ""
            SEL_WIKI_PAGE = ""
