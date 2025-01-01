"""
Rules page for Deadpool 2024.

This module displays the complete set of rules for the Deadpool game,
including entry requirements, scoring system, draft procedures, and
general guidelines. It requires authentication to view the rules.
"""

import logging
from typing import Final
import streamlit as st
from dp_utilities import mp_track_page_view

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PAGE_TITLE: Final[str] = "Rules"
PAGE_ICON: Final[str] = ":skull:"
PAGE_HEADER: Final[str] = "Rules :skull_and_crossbones:"
AUTH_KEY_RULES_LOGIN: Final[str] = "deadpool-app-login-rules"
AUTH_KEY_RULES_LOGOUT: Final[str] = "deadpool-app-logout-rules"
HOME_PAGE: Final[str] = "Home.py"

# Game Rules Text
RULES_TEXT: Final[str] = """
1. **Entry and Participation**:
    - All participants will draft their picks in January through this site.
    - The process will happen as a "Round Robin" based on the _Draft Order_
    - Participants select a list of 20 public figures they predict will pass away in 2024.
2. **Selection Criteria**:
    - Only public figures (celebrities, politicians, athletes, etc.) may be selected.
    - At least 50% of the players must know each selection, or be easily validated from Wikipedia.
    - You cannot pick Willie Nelson.  He is the new Betty White.
3. **Points System**:
    - The total points of the death will be calculated as **50 + (100-AGE)**.
    - E.g., the death of a person who's 90 years old will be 60 points.
    - First Blood will be awarded an additional **25 points**.
    - Last Blood will be awarded an additional **25 points**.
    - At the end of each calendar quarter, the person with the most points in that calendar quarter will be awarded **5 points**.
    - If you pick a dead person, which will be checked automatically after the draft finishes, you will lose that pick and receive 0 points.
4. **Re-Ups**:
    - One you have one of your picks die, you will automatically be granted another pick. All players shall have 20 alive picks at any given time.
5. **Duration**:
    - The dead pool runs from January 1, 2024, to December 31, 2024, at Midnight.
    - The draft will happen in January at a time condusive to participants.
    - Given the new system, we should close the draft no later than January 31 at Midnight.  The Arbiter will have the final say.
    - If any celebrity dies during the draft process, it's allowed if the draft was already recorded.
6. **Draft Order**:
    - Draft order has been computed to weigh the prior year's draft order and the number of points scored by the player.  The high draft order and higher scores penalized your spot in the new order.
    - Additionally, a random number has been applied for those who came later, which helps shuffle users who didn't play a little last year.
7. **Privacy and Confidentiality**:
    - Participant information must be kept confidential.
    - Lists of predictions should not be publicized or shared outside the pool.
8. **Dispute Resolution**:
    - The Arbiter's decision is final in all cases of disputes.
"""

ARBITER_SIGNATURE: Final[str] = "I have Spoken!  Signed the Arbiter"

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


def display_rules() -> None:
    """Display the complete set of game rules and Arbiter's signature."""
    st.markdown(RULES_TEXT)
    st.write(ARBITER_SIGNATURE)


def handle_authentication() -> None:
    """Handle user authentication and display appropriate content."""
    if st.session_state.get("authentication_status") is not None:
        try:
            # Setup authentication
            authenticator = st.session_state.get("authenticator")
            authenticator.logout(location="sidebar", key=AUTH_KEY_RULES_LOGOUT)
            authenticator.login(location="unrendered", key=AUTH_KEY_RULES_LOGIN)
            
            mp_track_page_view(PAGE_TITLE)
            
            # Get user information
            name = st.session_state.name
            email = st.session_state.email
            logger.info(f"Displaying rules for authenticated user: {email}")
            
            # Display user info and rules
            display_user_info(name, email)
            display_rules()
            
        except Exception as e:
            error_msg = f"Error displaying rules: {str(e)}"
            logger.error(error_msg)
            st.error(error_msg)
    else:
        logger.warning("Unauthenticated user attempted to access rules")
        st.warning("Please use the button below to navigate to Home and log in.")
        st.page_link(HOME_PAGE, label="Home", icon="🏠")
        st.stop()


def main() -> None:
    """Main function to handle the rules page flow."""
    logger.info("Starting rules page")
    handle_authentication()


if __name__ == "__main__":
    main()
