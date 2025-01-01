"""
Main page for Drafting new picks.

This module handles the drafting interface where users can submit their celebrity picks
for the deadpool game. It includes functionality for:
- Validating user turns
- Submitting draft picks
- Checking for duplicates
- Notifying users via SMS
"""

from datetime import datetime
import uuid
import logging
from typing import Tuple, List
import streamlit as st
from snowflake.connector import SnowflakeConnection
import pandas as pd
from dp_utilities import (
    has_fuzzy_match,
    send_sms,
    load_snowflake_table,
    snowflake_connection_helper,
    mp_track_page_view
)

# Constants
PAGE_TITLE = "Drafting"
PAGE_ICON = ":skull:"
DRAFT_YEAR = datetime.now().year
WEBSITE_URL = "https://deadpool.streamlit.app/Drafting"
MIN_PICK_LENGTH = 2
MAX_PICK_LENGTH = 255

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL Queries
SQL_INSERT_PEOPLE = """
INSERT INTO people (id, name, wiki_page)
VALUES (%s, %s, %s)
"""

SQL_INSERT_PLAYER_PICKS = """
INSERT INTO player_picks (player_id, year, people_id, timestamp)
VALUES (%s, %s, %s, %s)
"""

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)


def submitted() -> None:
    """Set the submission state to True."""
    st.session_state.submitted = True


def reset() -> None:
    """Reset the submission state to False."""
    st.session_state.submitted = False


def draft_logic(current_email: str, conn: SnowflakeConnection) -> Tuple[bool, str]:
    """Check if the current user is the person who will draft next.

    Args:
        current_email: Email of the current logged in person
        conn: Snowflake database connection

    Returns:
        Tuple containing:
            - bool: True if it's the person's turn to draft
            - str: Next user's ID if it's their turn, empty string otherwise
    """
    df_draft = load_snowflake_table(conn, "draft_next")

    if df_draft.empty:
        st.write(f"And with that the {DRAFT_YEAR} Draft is over!")
        return False, ""

    next_user = df_draft["EMAIL"].iloc[0]
    next_user_id = df_draft["ID"].iloc[0]

    if current_email == next_user:
        return True, next_user_id

    st.write("It is not your turn. Please come back when it is.")
    return False, ""


def validate_pick(pick: str) -> bool:
    """Validate the draft pick name.

    Args:
        pick: The celebrity name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not MIN_PICK_LENGTH <= len(pick) <= MAX_PICK_LENGTH:
        st.error(
            f"Pick must be between {MIN_PICK_LENGTH} and {MAX_PICK_LENGTH} characters long."
        )
        return False

    if not all(c.isalnum() or c.isspace() or c in ".-'" for c in pick):
        st.error(
            "Pick contains invalid characters. Only letters, numbers, spaces, hyphens, periods, and apostrophes are allowed."
        )
        return False

    return True


def handle_draft_submission(
    pick: str,
    next_user_id: str,
    conn: SnowflakeConnection,
    df_picks: pd.DataFrame,
    df_all_people: pd.DataFrame,
    opted_in_numbers: List[str],
    user_name: str,
) -> None:
    """Handle the draft pick submission process.

    Args:
        pick: The celebrity name being drafted
        next_user_id: ID of the user making the pick
        conn: Snowflake database connection
        df_picks: DataFrame of current year's picks
        df_all_people: DataFrame of all people in database
        opted_in_numbers: List of phone numbers opted in for notifications
        user_name: Name of the user making the pick
    """
    if not pick or not validate_pick(pick):
        return

    logger.info(f"Processing draft submission for pick: {pick}")

    # Check for duplicate picks this year
    logger.debug("Checking for duplicate picks")
    existing_person, _ = has_fuzzy_match(pick, df_picks, "NAME")
    if existing_person:
        st.write(
            """That pick has already been taken, please try again. Please review the "Draft Picks" page for more information."""
        )
        return

    try:
        # Process the pick
        wiki_page = pick.replace(" ", "_")
        timestamp = datetime.now(datetime.timezone.utc)

        # Check against historical picks
        existing_person, existing_id = has_fuzzy_match(pick, df_all_people, "NAME")
        new_id = existing_id if existing_person else uuid.uuid4()

        # Add new person if they don't exist
        if not existing_person:
            conn.cursor().execute(SQL_INSERT_PEOPLE, (new_id, pick, wiki_page))

        # Record the pick
        conn.cursor().execute(
            SQL_INSERT_PLAYER_PICKS,
            (next_user_id, DRAFT_YEAR, new_id, timestamp),
        )

        # Display confirmation
        st.caption("Database query executed")
        st.caption(
            f"{new_id}, {pick}, {next_user_id}, {wiki_page}, {DRAFT_YEAR}, {timestamp}"
        )

        # Send notifications
        send_draft_notifications(pick, user_name, opted_in_numbers, conn)

        st.caption("Draft pick complete")
        reset()

    except Exception as e:
        st.error(f"Error processing draft pick: {str(e)}")
        reset()


def send_draft_notifications(
    pick: str,
    user_name: str,
    opted_in_numbers: List[str],
    conn: SnowflakeConnection,
) -> None:
    """Send SMS notifications about the draft pick.

    Args:
        pick: The celebrity name that was drafted
        user_name: Name of the user who made the pick
        opted_in_numbers: List of phone numbers opted in for notifications
        conn: Snowflake database connection
    """
    # Notify opted-in users about the pick
    pick_message = f"{user_name} has picked {pick}"
    send_sms(pick_message, opted_in_numbers)

    # Notify next player
    df_next_sms = load_snowflake_table(conn, "draft_next")
    if not df_next_sms.empty:
        next_name = df_next_sms["NAME"].iloc[0]
        next_sms = df_next_sms["SMS"].iloc[0]

        next_message = (
            f"{next_name} is next to pick. "
            f"Please log into the website at {WEBSITE_URL} to make your selection."
        )
        send_sms(next_message, [next_sms])
        st.caption("SMS messages sent")
    else:
        st.caption("No additional names")


def display_draft_notes():
    """Display important notes about the drafting process."""
    st.markdown(
        """
    **Notes**:
    - The system checks for duplicate entries and has built-in fuzzy matching of names entered.
      If it's a slight misspelling, the duplicate will be caught. If it's way off, the Arbiter
      must de-duplicate and resolve it after draft day. The person with the earlier timestamp
      on the pick will keep the pick. The other person will get to submit an additional pick.
    - Please do not pick a dead person. If you do, you will lose that pick and receive 0 points.
    """
    )


def main():
    """Main function to handle the drafting interface."""
    logger.info("Starting drafting interface")
    st.title("Drafting :skull_and_crossbones:")

    if st.session_state.get("authentication_status") is None:
        logger.warning("User not authenticated")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link("Home.py", label="Home", icon="🏠")
        st.stop()

    # Authentication setup
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-drafting")
    authenticator.login(location="unrendered", key="deadpool-app-login-drafting")
    
    mp_track_page_view(PAGE_TITLE)

    # User information
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    logger.info(f"User authenticated: {email}")
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    # Database connections and data loading
    conn = snowflake_connection_helper()
    df_picks = load_snowflake_table(conn, "picks_current_year")
    df_all_people = load_snowflake_table(conn, "people")
    df_opted = load_snowflake_table(conn, "draft_opted_in")
    opted_in_numbers = df_opted["SMS"].tolist()

    st.write("Current User:", email)

    # Check if it's user's turn
    is_next, next_user_id = draft_logic(email, conn)
    if is_next:
        st.subheader("Draft Picks:")
        with st.form("Draft Picks"):
            pick = st.text_input(
                "Please choose your celebrity pick:", "", key="celeb_pick"
            ).strip()
            st.form_submit_button("Submit", on_click=submitted)

    # Handle submission
    if "submitted" in st.session_state and st.session_state.submitted:
        handle_draft_submission(
            pick,
            next_user_id,
            conn,
            df_picks,
            df_all_people,
            opted_in_numbers,
            user_name,
        )
        st.divider()
        display_draft_notes()


if __name__ == "__main__":
    main()
