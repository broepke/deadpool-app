"""
Draft Pick Maintenance for Deadpool 2024.

This module provides tools to modify pick information, primarily focusing on
Wikipedia page links. It allows administrators to:
- Select and update pick information
- Fix Wikipedia links for better accuracy
- Update pick names and IDs
- Manage pick metadata

Features:
- Pick selection from dropdown
- Wikipedia link validation
- Form-based updates
- Real-time database updates
"""

import logging
from typing import Final, Dict, Optional, NamedTuple
import streamlit as st
import pandas as pd
from snowflake.connector import SnowflakeConnection
from dp_utilities import (
    load_snowflake_table,
    snowflake_connection_helper,
    mp_track_page_view,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PAGE_TITLE: Final[str] = "Draft Pick Maintenance"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "Draft Pick Maintenance :skull_and_crossbones:"
AUTH_KEY_PICK_MAINT_LOGIN: Final[str] = "deadpool-app-login-pick-maintenance"
AUTH_KEY_PICK_MAINT_LOGOUT: Final[str] = "deadpool-app-logout-pick-maintenance"
HOME_PAGE: Final[str] = "Home.py"

# Form Constants
MAX_INPUT_LENGTH: Final[int] = 256
WIKI_BASE_URL: Final[str] = "https://en.wikipedia.org/wiki/"

# SQL Queries
SQL_UPDATE_PICK: Final[str] = """
UPDATE people 
SET name = %s, wiki_page = %s, wiki_id = %s 
WHERE id = %s
"""

# Instructions Text
INSTRUCTIONS: Final[str] = """
Use this form to fix the Wikipedia links if they were not guessed properly by the code when loaded.  In some cases there are disambiguation data such as '(actor)' for common names or there can be other URL encoding for special characters in names.
1. Select a name.
2. Update the Wiki link only using the end of the URL such as '**Tina_Turner**' in https://en.wikipedia.org/wiki/Tina_Turner.
3. Submit your adjustments.
"""

# Page configuration
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.title(PAGE_HEADER)


class PickData(NamedTuple):
    """Container for pick data."""

    id: str
    name: str
    wiki_page: str
    wiki_id: str


def display_user_info(name: str, email: str) -> None:
    """Display user information in the sidebar.

    Args:
        name: User's display name
        email: User's email address
    """
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")


def load_pick_data(conn: SnowflakeConnection) -> pd.DataFrame:
    """Load pick data from Snowflake.

    Args:
        conn: Snowflake database connection

    Returns:
        DataFrame containing pick data
    """
    try:
        df_picks = load_snowflake_table(conn, "people")
        logger.info("Pick data loaded successfully")
        return df_picks
    except Exception as e:
        error_msg = f"Error loading pick data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def get_pick_details(df: pd.DataFrame, pick_name: str) -> Optional[PickData]:
    """Get details for a specific pick.

    Args:
        df: DataFrame containing all picks
        pick_name: Name of the selected pick

    Returns:
        PickData tuple if found, None otherwise
    """
    try:
        filtered_df = df[df["NAME"] == pick_name]
        if not filtered_df.empty:
            row = filtered_df.iloc[0]
            return PickData(
                id=row["ID"],
                name=row["NAME"],
                wiki_page=row["WIKI_PAGE"],
                wiki_id=row["WIKI_ID"],
            )
        logger.warning(f"No pick found with name: {pick_name}")
        return None
    except Exception as e:
        logger.error(f"Error getting pick details: {str(e)}")
        return None


def update_session_state(pick_data: Optional[PickData]) -> None:
    """Update session state with pick data.

    Args:
        pick_data: PickData tuple or None
    """
    if pick_data:
        st.session_state["reg_id"] = pick_data.id
        st.session_state["reg_name"] = pick_data.name
        st.session_state["reg_wiki_page"] = pick_data.wiki_page
        st.session_state["reg_wiki_id"] = pick_data.wiki_id
        logger.debug(f"Session state updated for pick: {pick_data.name}")
    else:
        # Clear session state
        for key in ["reg_id", "reg_name", "reg_wiki_page", "reg_wiki_id"]:
            st.session_state[key] = ""
        logger.debug("Session state cleared")


def get_current_pick_data() -> PickData:
    """Get current pick data from session state.

    Returns:
        PickData tuple with current values
    """
    try:
        return PickData(
            id=st.session_state.get("reg_id", ""),
            name=st.session_state.get("reg_name", ""),
            wiki_page=st.session_state.get("reg_wiki_page", ""),
            wiki_id=st.session_state.get("reg_wiki_id", ""),
        )
    except Exception as e:
        logger.error(f"Error getting current pick data: {str(e)}")
        return PickData("", "", "", "")


def update_pick(
    conn: SnowflakeConnection, pick_data: PickData, new_data: PickData
) -> None:
    """Update pick information in database.

    Args:
        conn: Snowflake database connection
        pick_data: Original pick data
        new_data: New pick data to save
    """
    try:
        conn.cursor().execute(
            SQL_UPDATE_PICK,
            (new_data.name, new_data.wiki_page, new_data.wiki_id, pick_data.id),
        )

        # Log the update
        logger.info(f"Pick updated: {pick_data.name} -> {new_data.name}")

        # Display confirmation
        st.caption("Database updated successfully")
        st.caption(f"Original Name: {pick_data.name}")
        st.caption(f"New Name: {new_data.name}")
        st.caption(f"New Wiki Page: {new_data.wiki_page}")
        st.caption(f"New Wiki ID: {new_data.wiki_id}")

    except Exception as e:
        error_msg = f"Error updating pick: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def display_pick_selection_form(df: pd.DataFrame) -> None:
    """Display form for selecting a pick to update.

    Args:
        df: DataFrame containing all picks
    """
    st.header("Pick Selection")

    pick_list = sorted(df["NAME"].to_list())

    with st.form("Pick to Update"):
        sel_pick = st.selectbox("Select a pick", pick_list, key="sel_selected_pick")
        submitted = st.form_submit_button("Choose pick")

        if submitted:
            pick_data = get_pick_details(df, sel_pick)
            update_session_state(pick_data)


def display_update_form(conn: SnowflakeConnection) -> None:
    """Display form for updating pick information.

    Args:
        conn: Snowflake database connection
    """
    st.header("Update Pick Information")

    current_data = get_current_pick_data()

    with st.form("Pick Data"):
        new_name = st.text_input(
            "Name:",
            current_data.name,
            MAX_INPUT_LENGTH,
            key="_reg_name",
        )
        new_wiki_page = st.text_input(
            "Wiki Page:", current_data.wiki_page, MAX_INPUT_LENGTH, key="_reg_wiki_page"
        )
        new_wiki_id = st.text_input(
            "Wiki ID:", current_data.wiki_id, key="_reg_wiki_id"
        )

        if st.form_submit_button("Submit"):
            new_data = PickData(
                id=current_data.id,
                name=new_name.strip(),
                wiki_page=new_wiki_page.strip(),
                wiki_id=new_wiki_id.strip(),
            )
            update_pick(conn, current_data, new_data)
            update_session_state(None)  # Clear form after update


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_PICK_MAINT_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_PICK_MAINT_LOGIN)
            
            mp_track_page_view(PAGE_TITLE)

            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            logger.info(f"Displaying pick maintenance for authenticated user: {email}")

            # Display user info and instructions
            display_user_info(name, email)
            st.markdown(INSTRUCTIONS)

            # Load and display forms
            conn = snowflake_connection_helper()
            df_picks = load_pick_data(conn)
            display_pick_selection_form(df_picks)
            display_update_form(conn)

        except Exception as e:
            error_msg = f"Error in pick maintenance page: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access pick maintenance")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the pick maintenance page flow."""
    logger.info("Starting pick maintenance page")
    handle_authentication()


if __name__ == "__main__":
    main()
