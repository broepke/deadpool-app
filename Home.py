"""
Streamlit main application for Deadpool 2024.

This module serves as the main entry point for the Deadpool application.
It handles user authentication, displays welcome messages, and provides
admin tools for configuration management.

Features:
- User authentication with cookie persistence
- Admin tools for configuration management
- Welcome message from The Arbiter
- Session state debugging for admins
"""

import logging
import time
from typing import Dict, Any
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError
import yaml
from yaml.loader import SafeLoader
from dp_utilities import is_admin, get_ld_context
import ldclient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PAGE_TITLE = "Deadpool"
PAGE_ICON = ":skull:"
APP_TITLE = "Deadpool 2024 :skull_and_crossbones:"
CONFIG_FILE = "config.yaml"
ARBITER_MESSAGE = "Greetings, savages. All judgements are final."
ARBITER_IMAGE = "arbiter.jpg"
ARBITER_IMAGE_CAPTION = "The Arbiter"

# Authentication Constants
AUTH_LOCATION_MAIN = "main"
AUTH_LOCATION_SIDEBAR = "sidebar"
AUTH_KEY_HOME_LOGIN = "deadpool-app-login-home"
AUTH_KEY_HOME_LOGOUT = "deadpool-app-logout-home"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.title(APP_TITLE)


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file.

    Returns:
        Dict containing the configuration data
    """
    try:
        with open(CONFIG_FILE) as file:
            config = yaml.load(file, Loader=SafeLoader)
            logger.info("Configuration loaded successfully")
            return config
    except Exception as e:
        error_msg = f"Failed to load configuration: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def setup_authentication(config: Dict[str, Any]) -> stauth.Authenticate:
    """Set up the authentication system.

    Args:
        config: Configuration dictionary containing auth settings

    Returns:
        Configured authenticator object
    """
    try:
        authenticator = stauth.Authenticate(
            credentials=config["credentials"],
            cookie_name=config["cookie"]["name"],
            cookie_key=config["cookie"]["key"],
            cookie_expiry_days=config["cookie"]["expiry_days"],
            auto_hash=True,
        )
        logger.info("Authentication system initialized")
        return authenticator
    except Exception as e:
        error_msg = f"Failed to setup authentication: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        st.stop()


def display_arbiter_message(user_name: str) -> None:
    """Display the Arbiter's message and image.

    Args:
        user_name: Name of the current user
    """
    try:
        start_time = time.time()
        # Future enhancement: Uncomment to get dynamic message
        # output = the_arbiter(prompt, arbiter_version="base")
        output = ARBITER_MESSAGE

        end_time = time.time()
        time_taken = end_time - start_time
        logger.debug(f"Arbiter message generated in {time_taken:.2f} seconds")

        st.markdown("**A message from The Arbiter:** " + output)
        st.image(ARBITER_IMAGE, ARBITER_IMAGE_CAPTION)
    except Exception as e:
        logger.error(f"Error displaying Arbiter message: {str(e)}")
        st.write(f"Welcome Back, {user_name}")


def display_admin_tools() -> None:
    """Display admin tools if user has admin access."""
    st.subheader("Admin Tools")

    def download_config() -> None:
        """Create download button for config file."""
        try:
            config_data = yaml.dump(st.session_state["config"])
            st.download_button(
                label="Download Updated Config",
                data=config_data,
                file_name=CONFIG_FILE,
                mime="text/yaml",
                icon="📥",
            )
        except Exception as e:
            logger.error(f"Error creating config download: {str(e)}")
            st.error("Failed to create config download")

    download_config()

    # Session State Debugging
    with st.expander("Session State for Debugging", icon="💾"):
        st.session_state


def main() -> None:
    """Main function to handle the application flow."""
    # Load configuration and setup authentication
    config = load_config()
    authenticator = setup_authentication(config)

    # Store in session state for cross-page access
    st.session_state["authenticator"] = authenticator
    st.session_state["config"] = config

    # Handle authentication
    try:
        authenticator.login(location=AUTH_LOCATION_MAIN, key=AUTH_KEY_HOME_LOGIN)
    except LoginError as e:
        logger.warning(f"Login error: {str(e)}")
        st.error(e)

    # Handle authenticated user
    if st.session_state["authentication_status"]:
        authenticator.logout(location=AUTH_LOCATION_SIDEBAR, key=AUTH_KEY_HOME_LOGOUT)

        # Set LaunchDarkly Context for the user and send a login event
        ld_context = get_ld_context()
        ldclient.get().track(
            event_name="deadpool-login", metric_value=1, context=ld_context
        )
        st.session_state["ld_context"] = ld_context

        # Display user information
        name = st.session_state.name
        email = st.session_state.email
        user_name = st.session_state.username
        logger.info(f"User authenticated: {email}")

        st.sidebar.write(f"Welcome, {name}")
        st.sidebar.write(f"Email: {email}")

        # Display Arbiter message
        display_arbiter_message(user_name)

        # Display admin tools if applicable
        if is_admin():
            logger.info(f"Admin access granted for user: {email}")
            display_admin_tools()

    # Handle unauthenticated user
    elif st.session_state["authentication_status"] is False:
        logger.warning("Failed login attempt")
        st.error("Username/password is incorrect")
    else:
        st.warning("Please enter your username and password")


if __name__ == "__main__":
    main()
