"""
Main page for Drafting new picks
"""

from datetime import datetime
import uuid
import streamlit as st
from dp_utilities import has_fuzzy_match
from dp_utilities import send_sms
from dp_utilities import load_snowflake_table
from dp_utilities import snowflake_connection_helper


st.set_page_config(page_title="Drafting", page_icon=":skull:")


def submitted():
    st.session_state.submitted = True


def reset():
    st.session_state.submitted = False


def draft_logic(current_email):
    """Check to see if the current user is the person who will draft next

    Args:
        email (str): email of the current logged in person

    Returns:
        bool: If the person should draft or not
        str: Next user's ID
    """
    # Get the table for the draft order
    df_draft = load_snowflake_table(conn, "draft_next")

    # Handle the condition when the table is empty
    try:
        next_user = df_draft["EMAIL"].iloc[0]
        next_user_id = df_draft["ID"].iloc[0]
        if current_email == next_user:
            return True, next_user_id

        st.write("It is not your turn. Please come back when it is.")
        return False, ""
    except IndexError:
        # Send out SMS and write to page.
        st.write("And with that the 2024 Draft is over!")
        return False, ""


st.title("Drafting :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-drafting")
    authenticator.login(location="unrendered", key="deadpool-app-login-drafting")
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    conn = snowflake_connection_helper()

    df_picks = load_snowflake_table(conn, "picks_current_year")
    # Convert into a list for fuzzy matching
    current_drafts = df_picks["NAME"].tolist()

    # Get a list of the people that opted into alerts
    df_opted = load_snowflake_table(conn, "draft_opted_in")
    # Filter for just this year
    # Convert into a list for fuzzy matching
    opted_in_numbers = df_opted["SMS"].tolist()

    st.write("Current User:", email)

    # Only allow this to be show and run if not their turn.
    is_next, next_user_id = draft_logic(email)
    if is_next:
        st.subheader("Draft Picks:")
        with st.form("Draft Picks"):
            pick = st.text_input(
                "Please choose your celebrity pick:", "", key="celeb_pick"
            )

            pick = pick.strip()

            st.form_submit_button("Submit", on_click=submitted)

else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()

# See: https://discuss.streamlit.io/t/submit-form-button-not-working/35059/2
if "submitted" in st.session_state:
    if st.session_state.submitted:
        try:
            st.write("Draft Pick:", pick)

            if not pick:
                st.write("Please enter a valid selection.")

            MATCH = has_fuzzy_match(pick, current_drafts)

            if MATCH:
                st.write(
                    """That pick has already been taken, please try again. Please review the "Draft Picks" page for more information."""  # noqa: E501
                )

            else:
                # Set up a coupld of variables for the query
                new_id = uuid.uuid4()
                wiki_page = pick.replace(" ", "_")
                DRAFT_YEAR = datetime.now().year
                timestamp = datetime.now(datetime.timezone.utc)

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

                sms_message = user_name + " has picked " + pick
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
                    st.caption("No additional names")

                st.caption("Draft pick complete")

                reset()

        except Exception as e:
            st.caption(f"Please try your pick again.  Error: {e}")
            reset()

    st.divider()

    st.markdown(
        """
    **Notes**:
    - The system checks for duplicate entries and has built-in fuzzy matching of names entered.  If it's a slight misspelling, the duplicate will be caught.  If it's way off, the Arbiter must de-duplicate and resolve it after draft day.  The person with the earlier timestamp on the pick will keep the pick.  The other person will get to submit an additional pick.
    - Please do not pick a dead person.  If you do, you will lose that pick and receive 0 points.
    """  # noqa: E501
    )
