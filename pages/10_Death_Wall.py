"""
Death Wall Display for Deadpool 2024.

This module displays information about deceased picks, including:
- Birth and death dates
- Biographical information
- Images (when available)
- Search functionality
- Paginated results

Features:
- Real-time Wikidata queries
- Cached responses
- Search capabilities
- Responsive layout
"""

import logging
from typing import Final, Dict, List, Optional
from functools import lru_cache
import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
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
PAGE_TITLE: Final[str] = "Death Wall"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "Death Wall :skull_and_crossbones:"
AUTH_KEY_DEATH_WALL_LOGIN: Final[str] = "deadpool-app-login-death-wall"
AUTH_KEY_DEATH_WALL_LOGOUT: Final[str] = "deadpool-app-logout-death-wall"
HOME_PAGE: Final[str] = "Home.py"

# Wikidata Constants
WIKIDATA_ENDPOINT: Final[str] = "https://query.wikidata.org/sparql"
SPARQL_QUERY: Final[str] = """
SELECT ?personLabel ?birthDate ?deathDate ?image ?description
WHERE {{
wd:{wiki_id} wdt:P569 ?birthDate.
wd:{wiki_id} wdt:P570 ?deathDate.
OPTIONAL {{ wd:{wiki_id} wdt:P18 ?image. }}
OPTIONAL {{ wd:{wiki_id} schema:description ?description. FILTER(LANG(?description) = "en") }}
SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}}
LIMIT 1
"""

# Pagination Constants
ITEMS_PER_PAGE: Final[int] = 10
DEFAULT_PAGE: Final[int] = 1

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


@lru_cache(maxsize=100)
def query_wikidata_by_id(wiki_id: str) -> List[Dict]:
    """Query Wikidata for person information.

    Args:
        wiki_id: Wikidata ID for the person

    Returns:
        List of dictionaries containing person data
    """
    try:
        sparql = SPARQLWrapper(WIKIDATA_ENDPOINT)
        query = SPARQL_QUERY.format(wiki_id=wiki_id)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        logger.debug(f"Wikidata query successful for ID: {wiki_id}")
        return results["results"]["bindings"]
    except Exception as e:
        error_msg = f"Error querying Wikidata for ID {wiki_id}: {str(e)}"
        logger.error(error_msg)
        return []


def format_date(date_str: Optional[str]) -> str:
    """Format the date string from full datetime to YYYY-MM-DD.

    Args:
        date_str: Date string to format

    Returns:
        Formatted date string
    """
    if not date_str:
        return "Unknown"
    return date_str.split("T")[0] if "T" in date_str else date_str


def display_person_info(row: pd.Series, data: List[Dict]) -> None:
    """Display information about a deceased person.

    Args:
        row: DataFrame row containing person data
        data: Wikidata query results for the person
    """
    try:
        if data:
            person = data[0]
            birth_date = format_date(person.get("birthDate", {}).get("value"))
            death_date = format_date(person.get("deathDate", {}).get("value"))
            image_url = person.get("image", {}).get("value")
            description = person.get("description", {}).get("value", "")

            st.subheader(row["NAME"])
            st.write(f"Born: {birth_date} - Died: {death_date}")
            st.write(description)
            if image_url:
                st.image(image_url, width=200)

            logger.debug(f"Person info displayed: {row['NAME']}")
        else:
            st.write(f"Could not find data for {row['NAME']}.")
            logger.warning(f"No Wikidata results for: {row['NAME']}")
    except Exception as e:
        error_msg = f"Error displaying person info for {row['NAME']}: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)


def load_deceased_data(conn: SnowflakeConnection) -> pd.DataFrame:
    """Load data for deceased picks from Snowflake.

    Args:
        conn: Snowflake database connection

    Returns:
        DataFrame containing deceased picks data
    """
    try:
        df = load_snowflake_table(conn, "picks_current_year")
        df_dead = df.loc[df["DEATH_DATE"].notnull()].sort_values(
            by="DEATH_DATE", ascending=False
        )
        logger.info(f"Loaded {len(df_dead)} deceased picks")
        return df_dead
    except Exception as e:
        error_msg = f"Error loading deceased data: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def filter_by_search(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Filter DataFrame based on search term.

    Args:
        df: DataFrame to filter
        search_term: Search term to filter by

    Returns:
        Filtered DataFrame
    """
    try:
        filtered_df = df[df["NAME"].str.contains(search_term, case=False, na=False)]
        logger.debug(
            f"Filtered results: {len(filtered_df)} matches for '{search_term}'"
        )
        return filtered_df
    except Exception as e:
        logger.error(f"Error filtering data: {str(e)}")
        return df


def display_pagination_info(start_idx: int, end_idx: int, total: int) -> None:
    """Display pagination information.

    Args:
        start_idx: Starting index
        end_idx: Ending index
        total: Total number of items
    """
    st.write(f"Showing {start_idx + 1}-{min(end_idx, total)} of {total} results")


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_DEATH_WALL_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_DEATH_WALL_LOGIN)
            
            mp_track_page_view(PAGE_TITLE)

            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            logger.info(f"Displaying death wall for authenticated user: {email}")

            # Display user info
            display_user_info(name, email)

            # Load data
            conn = snowflake_connection_helper()
            df_dead = load_deceased_data(conn)

            # Handle search
            search_term = st.text_input("Search for a person")
            if search_term:
                df_dead = filter_by_search(df_dead, search_term)

            # Handle pagination
            page_number = st.number_input("Page", min_value=1, value=DEFAULT_PAGE)
            start_idx = (page_number - 1) * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE

            # Display results in columns
            df_page = df_dead.iloc[start_idx:end_idx]
            col1, col2 = st.columns(2)

            for i, row in df_page.iterrows():
                data = query_wikidata_by_id(row["WIKI_ID"])
                with col1 if i % 2 == 0 else col2:
                    display_person_info(row, data)

            display_pagination_info(start_idx, end_idx, len(df_dead))

        except Exception as e:
            error_msg = f"Error in death wall page: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access death wall")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the death wall page flow."""
    logger.info("Starting death wall page")
    handle_authentication()


if __name__ == "__main__":
    main()
