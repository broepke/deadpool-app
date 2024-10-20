"""
Main page for Drafting new picks
"""

from datetime import datetime
import streamlit as st
from dp_utilities import check_password
from dp_utilities import has_fuzzy_match
from dp_utilities import send_sms
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper


st.set_page_config(page_title="Drafting", page_icon=":skull:")


def submitted():
    st.session_state.submitted = True


def reset():
    st.session_state.submitted = False


st.title("Auto Drafting :skull_and_crossbones:")

email, user_name, authenticated = check_password()
if authenticated:
    conn = snowflake_connection_helper()

    df_players = load_snowflake_table(conn, "draft_next")

    try:
        df_player = df_players["EMAIL"].iloc[0]

        df_picks = load_snowflake_table(conn, "picks")
        # Filter for just this year
        df_2024 = df_picks[df_picks["YEAR"] == 2024]
        # Convert into a list for fuzzy matching
        current_drafts = df_2024["NAME"].tolist()

        # Get a list of the people that opted into alerts
        df_opted = load_snowflake_table(conn, "draft_opted_in")
        # Get a list of SMS number for sending out text
        opted_in_numbers = df_opted["SMS"].tolist()

        st.caption("Pick for the next player in the queue")

        if email == "broepke@gmail.com":
            st.write("Drafting for:", df_player)
            st.subheader("Draft Picks:")

            with st.form("Draft Picks"):
                pick = st.text_input(
                    "Please choose your celebrity pick:",
                    "",
                    key="celeb_auto_pick",  # noqa: E501
                )

                pick = pick.strip()

                st.form_submit_button("Submit", on_click=submitted)
        else:
            st.write("You are not authorized to use this incredibly powerful tool.")  # noqa: E501
    except Exception as e:
        st.write("There are no additional players to draft for.")
        st.caption(f"Error: {str(e)}")

# See: https://discuss.streamlit.io/t/submit-form-button-not-working/35059/2
if "submitted" in st.session_state:
    if st.session_state.submitted:
        st.write("Draft Pick:", pick)

        if not pick:
            st.write("Please enter a valid selection.")

            reset()

        MATCH = has_fuzzy_match(pick, current_drafts)

        if MATCH:
            st.write(
                """That pick has already been taken, please try again. Please review the "Draft Picks" page for more information."""  # noqa: E501
            )

            reset()

        else:
            # Set up a coupld of variables for the query
            wiki_page = pick.replace(" ", "_")
            DRAFT_YEAR = 2024
            timestamp = datetime.now(datetime.timezone.utc)

            df_draft_next = load_snowflake_table(conn, "draft_next")
            next_user = df_draft_next["EMAIL"].iloc[0]
            next_user_name = df_draft_next["NAME"].iloc[0]
            next_user_id = df_draft_next["ID"].iloc[0]
            
            WRITE_QUERY = """
            INSERT INTO picks (name, picked_by, wiki_page, year, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """

            # Execute the query with parameters
            conn.cursor().execute(
                WRITE_QUERY,
                (pick, next_user_id, wiki_page, DRAFT_YEAR, timestamp),
            )

            st.caption("Datebase query executed")
            st.caption(
                pick
                + ", "
                + next_user_id
                + ", "
                + wiki_page
                + ", "
                + str(DRAFT_YEAR)
                + ", "
                + str(timestamp)
            )

            sms_message = next_user_name + " has picked " + pick
            send_sms(sms_message, opted_in_numbers)

            df_next_sms = load_snowflake_table(conn, "draft_next")

            try:
                next_name = df_next_sms["NAME"].iloc[0]
                next_email = df_next_sms["EMAIL"].iloc[0]
                next_sms = df_next_sms["SMS"].iloc[0]

                # Send alert to the next player
                next_sms_message = (
                    next_name
                    + """ is next to pick.  Please log into the website at https://deadpool.streamlit.app/Drafting to make your selection."""  # noqa: E501
                )
                send_sms(next_sms_message, [next_sms])

                st.caption("SMS messages sent")

            except IndexError:
                st.write("No additional names")

        st.caption("Draft pick complete")

        reset()
