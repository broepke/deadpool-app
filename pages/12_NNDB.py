"""
Notable Names Database (NNDB) Statistics for Deadpool 2024.

This module provides statistical analysis and visualizations of celebrity
mortality data, including:
- Age distribution of deceased celebrities
- Occupation-based mortality ratios
- Risk factor analysis
- Predictive modeling results

Features:
- Interactive charts
- Descriptive statistics
- Risk factor identification
- The Arbiter's predictions
"""

import logging
from typing import Final
import streamlit as st
import altair as alt
import pandas as pd
from snowflake.connector import SnowflakeConnection

from dp_utilities import (
    load_snowflake_table,
    run_snowflake_query,
    snowflake_connection_helper,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PAGE_TITLE: Final[str] = "NNDB Stats"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "NNDB :skull_and_crossbones:"
AUTH_KEY_NNDB_LOGIN: Final[str] = "deadpool-app-login-nndb"
AUTH_KEY_NNDB_LOGOUT: Final[str] = "deadpool-app-logout-nndb"
HOME_PAGE: Final[str] = "Home.py"
CHART_COLOR: Final[str] = "#F63366"
MAX_AGE: Final[int] = 100
TOP_PREDICTIONS: Final[int] = 20

# SQL Queries
SQL_OCCUPATION_RATIO: Final[str] = """
SELECT
    OCCUPATION,
    COUNT(CASE WHEN DEATH_DATE IS NOT NULL THEN 1 END) AS DECEASED_COUNT,
    COUNT(CASE WHEN DEATH_DATE IS NOT NULL THEN 1 END) /
    NULLIF(COUNT(CASE WHEN DEATH_DATE IS NULL THEN 1 END), 0) AS RATIO
FROM DEADPOOL.PROD.NNDB
WHERE OCCUPATION IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
LIMIT 15
"""

SQL_RISK_FACTORS: Final[str] = """
SELECT NAME, RISK_FACTORS, AGE
FROM DEADPOOL.PROD.NNDB
WHERE RISK_FACTORS IS NOT NULL
AND DEATH_DATE IS NULL
AND AGE IS NOT NULL
AND AGE < 101
GROUP BY 1, 2, 3
ORDER BY 3 DESC
LIMIT 200
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


def load_nndb_data(conn: SnowflakeConnection) -> pd.DataFrame:
    """Load and preprocess NNDB data.

    Args:
        conn: Snowflake database connection

    Returns:
        Preprocessed DataFrame
    """
    try:
        df_nndb = load_snowflake_table(conn, "nndb")
        df_nndb = df_nndb[df_nndb["AGE"] < MAX_AGE]
        
        # Add life status columns
        df_nndb["IS_ALIVE"] = df_nndb["DEATH_DATE"].isnull()
        df_nndb["IS_DECEASED"] = df_nndb["DEATH_DATE"].notnull()
        
        logger.info("NNDB data loaded and preprocessed successfully")
        return df_nndb
    except Exception as e:
        error_msg = f"Error loading NNDB data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def display_age_distribution(df: pd.DataFrame) -> None:
    """Display age distribution chart and statistics.

    Args:
        df: DataFrame containing deceased people
    """
    try:
        st.subheader("Number of People Who are Dead by Age")
        st.write(
            "Data from the Notable Names Database. The following charts "
            "represent statistics on celebrities."
        )

        # Create and display line chart
        age_line_chart = (
            alt.Chart(df)
            .mark_line()
            .encode(alt.X("AGE"), y="count()", color=alt.value(CHART_COLOR))
        )
        st.altair_chart(age_line_chart, use_container_width=True)

        # Display descriptive statistics
        st.subheader("Descriptive Statistics on Age")
        st.dataframe(df["AGE"].describe(), use_container_width=True)
        
        logger.debug("Age distribution displayed successfully")
    except Exception as e:
        error_msg = f"Error displaying age distribution: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def display_occupation_stats(conn: SnowflakeConnection) -> None:
    """Display occupation-based mortality statistics.

    Args:
        conn: Snowflake database connection
    """
    try:
        df_occupation = run_snowflake_query(conn, SQL_OCCUPATION_RATIO)
        df_occupation["RATIO"] = df_occupation["RATIO"].astype(float)
        df_occupation = df_occupation.sort_values(by="RATIO", ascending=False)

        st.subheader("Occupations: Most Alive/Dead Ratio in the DB")
        occupation_chart = (
            alt.Chart(df_occupation)
            .mark_bar()
            .encode(
                x="RATIO:Q",
                y=alt.Y("OCCUPATION:N", sort=None),
                color=alt.value(CHART_COLOR),
            )
        )
        st.altair_chart(occupation_chart, use_container_width=True)
        
        logger.debug("Occupation statistics displayed successfully")
    except Exception as e:
        error_msg = f"Error displaying occupation stats: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def display_risk_factors(conn: SnowflakeConnection) -> None:
    """Display risk factor analysis.

    Args:
        conn: Snowflake database connection
    """
    try:
        df_risk = run_snowflake_query(conn, SQL_RISK_FACTORS)
        st.subheader("High Risk People by Age")
        st.dataframe(df_risk, use_container_width=True)
        
        logger.debug("Risk factors displayed successfully")
    except Exception as e:
        error_msg = f"Error displaying risk factors: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def display_predictions(conn: SnowflakeConnection) -> None:
    """Display The Arbiter's predictions.

    Args:
        conn: Snowflake database connection
    """
    try:
        df_nndb_preds = load_snowflake_table(conn, "nndb_predictions")
        df_nndb_preds.drop(columns=["ID", "IS_DECEASED"], inplace=True)
        df_nndb_preds = (
            df_nndb_preds.sort_values("PREDICTION", ascending=False)
            .head(TOP_PREDICTIONS)
            .reset_index(drop=True)
        )

        st.subheader("The Arbiter's Picks for 2024 are as follows.")
        st.dataframe(df_nndb_preds, use_container_width=True)
        
        logger.debug("Predictions displayed successfully")
    except Exception as e:
        error_msg = f"Error displaying predictions: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_NNDB_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_NNDB_LOGIN)
            
            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            user_name = st.session_state.username
            logger.info(f"Displaying NNDB stats for authenticated user: {email}")
            
            # Display user info
            display_user_info(name, email)
            
            # Load data and display statistics
            conn = snowflake_connection_helper()
            df_nndb = load_nndb_data(conn)
            df_nndb_dead = df_nndb[df_nndb["IS_DECEASED"]]
            
            display_age_distribution(df_nndb_dead)
            display_occupation_stats(conn)
            display_risk_factors(conn)
            display_predictions(conn)
            
        except Exception as e:
            error_msg = f"Error in NNDB page: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access NNDB")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the NNDB page flow."""
    logger.info("Starting NNDB page")
    handle_authentication()


if __name__ == "__main__":
    main()
