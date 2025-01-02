"""
Main page for Drafting new picks
"""

from datetime import datetime
import uuid
import streamlit as st
from dp_utilities import (
    has_fuzzy_match,
    send_sms,
    load_snowflake_table,
    snowflake_connection_helper,
    is_admin,
    mp_track_page_view,
)

PAGE_TITLE = "Drafting"
PAGE_ICON = ":skull:"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)


def submitted():
    st.session_state.submitted = True


def reset():
    st.session_state.submitted = False


st.title("Auto Drafting :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-auto-draft")
    authenticator.login(location="unrendered", key="deadpool-app-login-auto-draft")
    
    mp_track_page_view(PAGE_TITLE)
    
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    conn = snowflake_connection_helper()

    df_players = load_snowflake_table(conn, "draft_next")

    try:
        df_player = df_players["EMAIL"].iloc[0]

        df_picks = load_snowflake_table(conn, "picks_current_year")
        # Convert into a list for fuzzy matching
        current_drafts = df_picks["NAME"].tolist()

        # Get a list of the people that opted into alerts
        df_opted = load_snowflake_table(conn, "draft_opted_in")
        # Get a list of SMS number for sending out text
        opted_in_numbers = df_opted["SMS"].tolist()

        st.caption("Pick for the next player in the queue")

        if is_admin():
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

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()

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
            new_id = str(uuid.uuid4())  # Convert UUID to string
            wiki_page = pick.replace(" ", "_")
            DRAFT_YEAR = datetime.now().year
            timestamp = datetime.now(datetime.timezone.utc)

            df_draft_next = load_snowflake_table(conn, "draft_next")
            next_user = df_draft_next["EMAIL"].iloc[0]
            next_user_name = df_draft_next["NAME"].iloc[0]
            next_user_id = df_draft_next["ID"].iloc[0]

            WRITE_PEOPLE_QUERY = """
            INSERT INTO people (id, name, wiki_page)
            VALUES (%s, %s, %s)
            """

            WRITE_PLAYER_PICKS_QUERY = """
            INSERT INTO player_picks (player_id, year, people_id, timestamp)
            VALUES (%s, %s, %s, %s)
            """

            # Execute the query with parameters
            conn.cursor().execute(
                WRITE_PEOPLE_QUERY,
                (new_id, pick, wiki_page),
            )

            # Execute the query with parameters
            conn.cursor().execute(
                WRITE_PLAYER_PICKS_QUERY,
                (next_user_id, DRAFT_YEAR, new_id, timestamp),
            )

            st.caption("Database query executed")
            st.caption(
                f"{new_id}, {pick}, {next_user_id}, {wiki_page}, {DRAFT_YEAR}, {timestamp}"
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
