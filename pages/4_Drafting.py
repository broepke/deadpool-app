"""
Main page for Unified Drafting.

This module handles the drafting interface where users and admins can submit celebrity picks
for the deadpool game. It includes functionality for:
- Regular user drafting
- Admin override drafting
- Validating user turns
- Submitting draft picks
- Checking for duplicates
- Notifying users via SMS
"""

import logging
from datetime import datetime, timezone
import uuid
from typing import Tuple, Any, List
import pandas as pd
import streamlit as st
from dp_utilities import (
    has_fuzzy_match,
    send_sms,
    load_snowflake_table,
    snowflake_connection_helper,
    is_admin,
    mp_track_page_view,
)

# Constants
PAGE_TITLE = "Drafting"
PAGE_ICON = ":skull:"
DRAFT_YEAR = datetime.now().year
WEBSITE_URL = "https://deadpool.streamlit.app/Drafting"
MIN_PICK_LENGTH = 2
MAX_PICK_LENGTH = 255

# SQL Queries
SQL_INSERT_PEOPLE = """
INSERT INTO people (id, name, wiki_page)
VALUES (%s, %s, %s)
"""

SQL_INSERT_PLAYER_PICKS = """
INSERT INTO player_picks (player_id, year, people_id, timestamp)
VALUES (%s, %s, %s, %s)
"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)


def submitted() -> None:
    """Set the submission state to True."""
    st.session_state.submitted = True


def reset() -> None:
    """Reset the submission state to False."""
    st.session_state.submitted = False


def draft_logic(current_email: str, conn: Any) -> Tuple[bool, str]:
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
    try:
        next_user = df_draft["EMAIL"].iloc[0]
        next_user_id = df_draft["ID"].iloc[0]
        if current_email == next_user:
            return True, next_user_id

        st.write("It is not your turn. Please come back when it is.")
        return False, ""
    except IndexError:
        st.write("And with that the 2024 Draft is over!")
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


def draft_pick(
    pick: str,
    user_info: Any,
    conn: Any,
    opted_in_numbers: List[str],
    current_drafts: List[str],
    user_name: str,
    admin_mode: bool = False
) -> None:
    """Handle the draft logic for both regular users and admins.
    
    Args:
        pick: The celebrity name being drafted
        user_info: User information (email for regular users, DataFrame for admin)
        conn: Snowflake database connection
        opted_in_numbers: List of phone numbers opted in for notifications
        current_drafts: List of already drafted celebrity names
        user_name: Name of the user making the pick
        admin_mode: Whether the draft is being made by an admin
    """
    logger.info(f"Processing draft submission for pick: {pick}")

    try:
        if not pick or not validate_pick(pick):
            return

        # Check for duplicate picks this year
        has_match, match_id = has_fuzzy_match(pick, current_drafts, "NAME")
        if has_match:
            st.error(
                """That pick has already been taken. Please try again. 
                Please review the "Draft Picks" page for more information."""
            )
            st.info(f"Match found: {match_id}")
            return

        # Check if person exists in database
        df_all_people = load_snowflake_table(conn, "people")
        existing_person, existing_id = has_fuzzy_match(pick, df_all_people, "NAME")
        
        # Use existing ID if person exists, otherwise generate new one
        person_id = existing_id if existing_person else str(uuid.uuid4())
        wiki_page = pick.replace(" ", "_")
        timestamp = datetime.now(timezone.utc)

        # Only insert new person if they don't exist
        if not existing_person:
            conn.cursor().execute(SQL_INSERT_PEOPLE, (person_id, pick, wiki_page))

        # Record the pick
        # For admin mode, get ID from DataFrame, otherwise use the provided user_info directly
        if isinstance(user_info, pd.DataFrame) and not user_info.empty:
            player_id = user_info["ID"].iloc[0]
        else:
            player_id = user_info
        conn.cursor().execute(
            SQL_INSERT_PLAYER_PICKS,
            (player_id, DRAFT_YEAR, person_id, timestamp),
        )

        # Send notifications
        send_draft_notifications(pick, user_name, opted_in_numbers, conn)
        
        st.success("Draft pick complete")
        reset()

    except Exception as e:
        logger.error(f"Error processing draft pick: {str(e)}")
        st.error(f"Error occurred: {str(e)}")
        reset()


def send_draft_notifications(
    pick: str,
    user_name: str,
    opted_in_numbers: List[str],
    conn: Any,
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
    if len(df_next_sms) > 0:
        next_name = df_next_sms["NAME"].iloc[0]
        next_sms = df_next_sms["SMS"].iloc[0]
        next_message = (
            f"{next_name} is next to pick. "
            f"Please log into the website at {WEBSITE_URL} to make your selection."
        )
        send_sms(next_message, [next_sms])
        logger.info("SMS notifications sent")
    else:
        logger.info("No additional players to notify")


def display_draft_notes() -> None:
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


def main() -> None:
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
    current_drafts = df_picks["NAME"].tolist()
    df_opted = load_snowflake_table(conn, "draft_opted_in")
    opted_in_numbers = df_opted["SMS"].tolist()

    if is_admin():
        logger.info("Admin mode detected")
        st.info("Admin Mode Enabled")
        df_players = load_snowflake_table(conn, "draft_next")
        
        try:
            df_player = df_players["EMAIL"].iloc[0]
            st.write("Drafting for:", df_player)
            with st.form("Draft Picks"):
                pick = st.text_input(
                    "Please choose the celebrity pick for the next player:",
                    "",
                    key="celeb_auto_pick",
                ).strip()

                if st.form_submit_button("Submit", on_click=submitted):
                    draft_pick(
                        pick, df_players, conn, opted_in_numbers, current_drafts,
                        user_name, admin_mode=True
                    )
                    st.divider()
                    display_draft_notes()
                    
        except IndexError:
            st.info("There are no additional players to draft for.")
            logger.info("No more players in draft queue")
            
        except Exception as e:
            logger.error(f"Error in admin mode: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
    else:
        logger.info("Regular user mode")
        st.write("Regular User Mode")
        is_next, next_user_id = draft_logic(email, conn)
        
        if is_next:
            st.subheader("Draft Picks:")
            with st.form("Draft Picks"):
                pick = st.text_input(
                    "Please choose your celebrity pick:", "", key="celeb_pick"
                ).strip()

                if st.form_submit_button("Submit", on_click=submitted):
                    draft_pick(
                        pick, next_user_id, conn, opted_in_numbers, current_drafts,
                        user_name, admin_mode=False
                    )
                    st.divider()
                    display_draft_notes()


if __name__ == "__main__":
    main()
