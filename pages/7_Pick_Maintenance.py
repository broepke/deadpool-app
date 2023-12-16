import streamlit as st
from Home import check_password


def save_value(key):
    st.session_state[key] = st.session_state["_" + key]


def get_value(key):
    st.session_state["_" + key] = st.session_state[key]


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
except:
    st.write("Please login again")

if email != "broepke@gmail.com":
    st.write("Not authorized")
else:
    st.title("Pick Maintenance Tools")
    st.markdown("""
                Use this form to fix the Wikipedia links if they were not guessed properly by the code when loaded.  In some cases there are disambiguation data such as '(actor)' for common names or there can be other URL encoding for special characters in names.
                1. Select a name.
                2. Update the Wiki link only using the end of the URL such as '**Tina_Turner**' in https://en.wikipedia.org/wiki/Tina_Turner.
                3. Submit your adjustments.
                """)

    # Initialize important varibles
    sel_name = ""
    sel_wiki_page = ""

    # Initialize connection.
    conn = st.connection("snowflake")

    # Get a list off all curent picks
    @st.cache_data
    def load_picks_table():
        session_picks = conn.session()
        return session_picks.table("picks").to_pandas()

    df_picks = load_picks_table()

    df_picks_2024 = df_picks[df_picks["YEAR"] == 2024]

    df_picks_list = df_picks_2024["NAME"].to_list()
    df_picks_list.sort()

    st.header("Pick Selection")

    # Load all the picks into a drop down for easy selection
    with st.form("Pick to Update"):
        sel_pick = st.selectbox("Select a pick", df_picks_list, key="sel_selected_pick")
        submitted = st.form_submit_button("Choose pick")

        if submitted:
            filtered_df = df_picks_2024[df_picks_2024["NAME"] == sel_pick]

            if not filtered_df.empty:
                sel_name = filtered_df.iloc[0]["NAME"]
                sel_wiki_page = filtered_df.iloc[0]["WIKI_PAGE"]

                st.session_state["reg_name"] = sel_name
                st.session_state["reg_wiki_page"] = sel_wiki_page

            else:
                print("No user found with the given email")

    st.header("Update Pick Information")

    with st.form("Registration"):
        try:
            sel_name = st.session_state["reg_name"]
            sel_wiki_page = st.session_state["reg_wiki_page"]
        except:
            sel_name = ""
            sel_wiki_page = ""

        sub_name = st.text_input(
            "First Name:",
            sel_name,
            256,
            key="_reg_name",
        )
        sub_wiki_page = st.text_input(
            "Last Name:", sel_wiki_page, 256, key="_reg_wiki_page"
        )

        submitted = st.form_submit_button("Submit")
        if submitted:
            write_query = (
                "UPDATE picks SET wiki_page = :1 WHERE name = :2 AND year = 2024"
            )

            # # Execute the query with parameters
            conn.cursor().execute(
                write_query,
                (sub_wiki_page, sub_name),
            )

            st.write(write_query)
            st.write(sub_name)
            st.write(sub_wiki_page)
