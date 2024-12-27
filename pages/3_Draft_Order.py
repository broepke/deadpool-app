"""
Draft Order page for Deadpool 2024.

This module displays the draft order for the 2024 season, including:
- The computed draft order based on prior year's performance
- Explanation of the draft order calculation
- Current draft positions for all players

The draft order is calculated using a combination of:
- Previous draft position
- Points scored
- Random factor for new players
"""

import logging
from typing import Final
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
PAGE_TITLE: Final[str] = "Draft Order"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "Draft Order :skull_and_crossbones:"
AUTH_KEY_DRAFT_ORDER_LOGIN: Final[str] = "deadpool-app-login-draft-order"
AUTH_KEY_DRAFT_ORDER_LOGOUT: Final[str] = "deadpool-app-logout-draft-order"
HOME_PAGE: Final[str] = "Home.py"

# Draft Order Explanation Text
DRAFT_ORDER_EXPLANATION: Final[str] = """
**Draft Order**:
- Draft order has been computed to weigh the prior year's draft order and the number of points scored by the player.  The high draft order and higher scores penalized your spot in the new order.
- Additionally, a random number has been applied for those who came later, which helps shuffle users who didn't play a little last year.
- All numbers are normalized between 0 and 1.
- Finally the calculation is: `ORDER + RANDOM + (SCORE * -1)`.
"""

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


def load_draft_order(conn: SnowflakeConnection) -> pd.DataFrame:
    """Load and sort the draft order data.

    Args:
        conn: Snowflake database connection

    Returns:
        DataFrame containing sorted draft order
    """
    try:
        df_ord = load_snowflake_table(conn, "draft_selection")
        logger.info("Draft order data loaded successfully")
        return df_ord.sort_values(by="SCORE", ascending=False).reset_index(drop=True)
    except Exception as e:
        error_msg = f"Error loading draft order: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def display_draft_order(df: pd.DataFrame) -> None:
    """Display the draft order information and data.

    Args:
        df: DataFrame containing the draft order data
    """
    st.subheader("2024 Draft Order")
    st.markdown(DRAFT_ORDER_EXPLANATION)
    st.dataframe(df, use_container_width=True)


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_DRAFT_ORDER_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_DRAFT_ORDER_LOGIN)
            
            mp_track_page_view(PAGE_TITLE)

            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            logger.info(f"Displaying draft order for authenticated user: {email}")

            # Display user info
            display_user_info(name, email)

            # Load and display draft order
            conn = snowflake_connection_helper()
            df_sorted = load_draft_order(conn)
            display_draft_order(df_sorted)

        except Exception as e:
            error_msg = f"Error displaying draft order: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access draft order")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the draft order page flow."""
    logger.info("Starting draft order page")
    handle_authentication()


if __name__ == "__main__":
    main()
