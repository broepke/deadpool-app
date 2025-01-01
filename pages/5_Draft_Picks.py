"""
Draft Picks Display for Deadpool 2024.

This module displays all draft picks for the Deadpool game, including:
- Current year's draft picks
- Picks organized by person
- Historical picks from previous year
- Comprehensive view of all selections

Features:
- Real-time data from Snowflake
- Multiple view options for draft picks
- Historical comparison capabilities
"""

import logging
from typing import Final, Dict
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
PAGE_TITLE: Final[str] = "All Draft Picks"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "Draft Picks :skull_and_crossbones:"
AUTH_KEY_DRAFT_PICKS_LOGIN: Final[str] = "deadpool-app-login-draft-picks"
AUTH_KEY_DRAFT_PICKS_LOGOUT: Final[str] = "deadpool-app-logout-draft-picks"
HOME_PAGE: Final[str] = "Home.py"

# Page configuration
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.title(PAGE_HEADER)


def display_user_info(name: str, email: str) -> None:
    """Display user information in the sidebar.

    Args:
        name: User's display name
        email: User's email address
    """
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")


def load_draft_data(conn: SnowflakeConnection) -> Dict[str, pd.DataFrame]:
    """Load all required draft data from Snowflake.

    Args:
        conn: Snowflake database connection

    Returns:
        Dictionary containing different draft data DataFrames
    """
    try:
        # Load current and historical picks
        df_current = load_snowflake_table(conn, "picks_current_year")
        df_2024 = load_snowflake_table(conn, "picks_twenty_four")
        # df_2023 = load_snowflake_table(conn, "picks_twenty_three")

        # Load picks by person
        df_picks = load_snowflake_table(conn, "draft")
        df_picks.drop(columns="ID", inplace=True)

        logger.info("Draft data loaded successfully")
        return {"current": df_current, "historical": df_2024, "by_person": df_picks}
    except Exception as e:
        error_msg = f"Error loading draft data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def display_draft_picks(data: Dict[str, pd.DataFrame]) -> None:
    """Display all draft pick information in various formats.

    Args:
        data: Dictionary containing different draft pick DataFrames
    """
    try:
        # Display current picks
        st.header("Current Draft Picks:")
        st.dataframe(data["current"])

        # Display picks by person
        st.subheader("Current Draft Picks by Person")
        st.dataframe(data["by_person"], use_container_width=True)

        st.divider()

        # Display year-specific picks
        st.header("2024 Draft Picks:")
        st.dataframe(data["current"])

        st.header("2023 Draft Picks:")
        st.dataframe(data["historical"], use_container_width=True)

        logger.debug("Draft picks displayed successfully")
    except Exception as e:
        error_msg = f"Error displaying draft picks: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_DRAFT_PICKS_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_DRAFT_PICKS_LOGIN)
            
            mp_track_page_view(PAGE_TITLE)

            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            logger.info(f"Displaying draft picks for authenticated user: {email}")

            # Display user info
            display_user_info(name, email)

            # Load and display draft data
            conn = snowflake_connection_helper()
            draft_data = load_draft_data(conn)
            display_draft_picks(draft_data)

        except Exception as e:
            error_msg = f"Error in draft picks page: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access draft picks")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the draft picks page flow."""
    logger.info("Starting draft picks page")
    handle_authentication()


if __name__ == "__main__":
    main()
