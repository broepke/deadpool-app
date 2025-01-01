"""
Leaderboard Display for Deadpool 2024.

This module displays various leaderboards and statistics for the Deadpool game, including:
- Current year standings
- Historical results
- Visual representations of scores
- Comparative statistics

Features:
- Real-time data from Snowflake
- Interactive charts and tables
- Historical comparisons
- Highlighted maximum scores
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
PAGE_TITLE: Final[str] = "Leaderboard"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "Leaderboards :skull_and_crossbones:"
AUTH_KEY_LEADERBOARD_LOGIN: Final[str] = "deadpool-app-login-leaderboard"
AUTH_KEY_LEADERBOARD_LOGOUT: Final[str] = "deadpool-app-logout-leaderboard"
HOME_PAGE: Final[str] = "Home.py"

# Chart Constants
CHART_COLOR: Final[str] = "#F63366"
CHART_X_COLUMN: Final[str] = "PLAYER"
CHART_Y_COLUMN: Final[str] = "TOTAL"
COLUMNS_TO_DROP: Final[list] = ["EMAIL", "ID"]

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


def load_score_data(conn: SnowflakeConnection) -> Dict[str, pd.DataFrame]:
    """Load all required score data from Snowflake.

    Args:
        conn: Snowflake database connection

    Returns:
        Dictionary containing different score DataFrames
    """
    try:
        # Load scores for different time periods
        df_score_current = load_snowflake_table(conn, "score_current_year")
        df_score_2024 = load_snowflake_table(conn, "score_twenty_four")
        df_score_2023 = load_snowflake_table(conn, "score_twenty_three")

        # Clean up dataframes
        for df in [df_score_current, df_score_2024, df_score_2023]:
            df.drop(columns=COLUMNS_TO_DROP, inplace=True)

        logger.info("Score data loaded successfully")
        return {
            "current": df_score_current,
            "2024": df_score_2024,
            "2023": df_score_2023,
        }
    except Exception as e:
        error_msg = f"Error loading score data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def display_leaderboard(title: str, data: pd.DataFrame) -> None:
    """Display a single leaderboard section with table and chart.

    Args:
        title: Header text for the section
        data: DataFrame containing the score data
    """
    try:
        st.header(title)

        # Display table with highlighted maximum
        st.dataframe(
            data.style.highlight_max(axis=0, subset=[CHART_Y_COLUMN]),
            use_container_width=True,
        )

        # Display bar chart
        st.bar_chart(data=data, x=CHART_X_COLUMN, y=CHART_Y_COLUMN, color=CHART_COLOR)

        logger.debug(f"Leaderboard displayed successfully: {title}")
    except Exception as e:
        error_msg = f"Error displaying leaderboard {title}: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def display_all_leaderboards(data: Dict[str, pd.DataFrame]) -> None:
    """Display all leaderboards in sequence.

    Args:
        data: Dictionary containing different score DataFrames
    """
    try:
        display_leaderboard("Current Leaderboard:", data["current"])
        display_leaderboard("2024 Results", data["2024"])
        display_leaderboard("2023 Results", data["2023"])
        logger.debug("All leaderboards displayed successfully")
    except Exception as e:
        error_msg = f"Error displaying leaderboards: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_LEADERBOARD_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_LEADERBOARD_LOGIN)

            mp_track_page_view(PAGE_TITLE)
            
            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            logger.info(f"Displaying leaderboards for authenticated user: {email}")

            # Display user info
            display_user_info(name, email)

            # Load and display leaderboard data
            conn = snowflake_connection_helper()
            score_data = load_score_data(conn)
            display_all_leaderboards(score_data)

        except Exception as e:
            error_msg = f"Error in leaderboard page: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access leaderboards")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the leaderboard page flow."""
    logger.info("Starting leaderboard page")
    handle_authentication()


if __name__ == "__main__":
    main()
