"""
Utility functions for the Deadpool application providing database connectivity,
authentication, messaging, and other shared functionality. This module contains
reusable components that are used across different parts of the application.

Functions in this module handle:
- Snowflake database connections and queries
- Session state management
- User authentication and authorization
- SMS messaging via Twilio
- Feature flag management via LaunchDarkly
- Natural language processing utilities
"""

import requests
import pandas as pd
import snowflake.connector
from fuzzywuzzy import fuzz
from twilio.rest import Client
import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import ldclient
from ldclient import Context
from ldclient.config import Config
from mixpanel import Mixpanel


# Function to load the private key from secrets
def load_private_key_from_secrets(private_key_str):
    """Function to take a plain text string of an RSA Private key and convert
       into the proper format needed for a connection string.

    Args:
        private_key_str (str): The original and full RSA key with begin and end strings + line breaks

    Returns:
        RSA Key: binary encoded RSA key from string
    """
    private_key = serialization.load_pem_private_key(
        private_key_str.encode(),
        password=None,
        backend=default_backend(),
    )
    return private_key


@st.cache_resource(ttl=3600)
def snowflake_connection_helper():
    """Creates and returns a cached connection to Snowflake using credentials from streamlit secrets.
    
    The connection uses RSA key authentication and is cached for 1 hour to prevent
    excessive connection creation. All connection parameters are retrieved from
    streamlit secrets.

    Returns:
        snowflake.connector.connection.SnowflakeConnection: A connection object to Snowflake
    """
    # Load the private key from secrets directly inside the function to avoid passing it as an argument
    private_key = load_private_key_from_secrets(
        st.secrets["connections"]["snowflake"]["private_key"]
    )

    # Set up the connection using the formatted private key, without caching the private key object
    conn = snowflake.connector.connect(
        account=st.secrets["connections"]["snowflake"]["account"],
        user=st.secrets["connections"]["snowflake"]["user"],
        private_key=private_key,
        role=st.secrets["connections"]["snowflake"]["role"],
        warehouse=st.secrets["connections"]["snowflake"]["warehouse"],
        database=st.secrets["connections"]["snowflake"]["database"],
        schema=st.secrets["connections"]["snowflake"]["schema"],
    )

    return conn


def save_value(key):
    """Updates the session state with a permanent value from a temporary input.
    
    Args:
        key (str): The key name in the session state to update. The function will
                  copy the value from '_key' to 'key' in the session state.
    """
    st.session_state[key] = st.session_state["_" + key]


def load_snowflake_table(_conn, table):
    """Loads a specific Snowflake table using SQL.

    Executes a SELECT * query on the specified table or view and returns
    all rows as a pandas DataFrame. The function handles column name extraction
    and data conversion automatically.

    Args:
        _conn (snowflake.connector.connection.SnowflakeConnection): Active Snowflake connection
        table (str): Name of the table or view to query (no database or schema needed)

    Returns:
        pandas.DataFrame: Complete contents of the specified table/view
    """
    query = f"SELECT * FROM {table}"

    # Use cursor to execute the query
    with _conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()
        # Get column names from cursor
        columns = [desc[0] for desc in cur.description]

    # Convert the result to a Pandas DataFrame
    df = pd.DataFrame(result, columns=columns)

    return df


def run_snowflake_query(_conn, query):
    """Executes a SQL query on Snowflake and returns the results as a pandas DataFrame.
    
    Args:
        _conn (snowflake.connector.connection.SnowflakeConnection): Active Snowflake connection
        query (str): SQL query to execute
        
    Returns:
        pandas.DataFrame: Results of the query as a DataFrame
    """
    with _conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetch_pandas_all()
        return result


def is_admin():
    """Checks if the current user has admin privileges.
    
    Examines the user's roles in the session state to determine if they
    have admin access. Returns False if there's an error accessing the
    session state or if the admin role is not present.
    
    Returns:
        bool: True if user has admin role, False otherwise
    """
    try:
        # Safely retrieve the roles or default to an empty list
        user_roles = st.session_state.get("roles", []) or []

        # Check if 'admin' is in the roles
        if "admin" in user_roles:
            return True
        return False

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return False


def the_arbiter(prompt, arbiter_version="main"):
    """Chatbot API call to LangChain LLM.

    Makes an API call to a specified version of the LLM chatbot service.
    Handles different API endpoints based on the specified version.

    Args:
        prompt (str): The question or prompt to send to the LLM
        arbiter_version (str, optional): Version of the LLM to use.
            Can be "main" or "base". Defaults to "main".

    Returns:
        str: Text response from the LLM, or error message if the call fails
    """

    if arbiter_version == "main":
        apify_api_url = st.secrets["apify"]["main_api"]
        apify_bearer = st.secrets["apify"]["main_bearer"]
    elif arbiter_version == "base":
        apify_api_url = st.secrets["apify"]["base_api"]
        apify_bearer = st.secrets["apify"]["base_bearer"]
    else:
        apify_api_url = st.secrets["apify"]["main_api"]
        apify_bearer = st.secrets["apify"]["main_bearer"]

    headers = {"Authorization": apify_bearer}
    payload = {
        "question": prompt,
    }

    try:
        response = requests.post(
            apify_api_url, headers=headers, json=payload, timeout=60
        )
        output = response.json()
        return output["text"]
    except Exception as e:
        return "The Arbiter is sleeping: " + str(e)


def has_fuzzy_match(value, df, column, threshold=85):
    """Performs fuzzy text matching using natural language processing.

    Uses the FuzzyWuzzy library to find approximate string matches,
    accounting for typos, case differences, and word order variations.
    The function compares the input value against all entries in the
    specified DataFrame column and returns both match status and ID.

    Args:
        value (str): The string value to search for
        df (pandas.DataFrame): DataFrame containing potential matches
        column (str): Name of the column in df to search within
        threshold (int, optional): Minimum similarity score (0-100) required
            for a match. Higher values require closer matches. Defaults to 85.

    Returns:
        tuple: (bool, int or None) - First element indicates if a match was found,
            second element is the ID of the matched row or None if no match
    """
    # Handle empty dataframe/list case
    if isinstance(df, pd.DataFrame):
        if len(df) == 0:
            return False, None
        value_set = df[column].tolist()
    elif isinstance(df, list):
        if not df:
            return False, None
        value_set = df
    else:
        raise ValueError(f"Expected DataFrame or list, got {type(df)}")

    for index, item in enumerate(value_set):
        if fuzz.token_sort_ratio(value.lower(), item.lower()) >= threshold:
            # Get ID differently based on input type
            if isinstance(df, pd.DataFrame):
                person_id = df.iloc[index]["ID"]
            else:
                # For list input, we can't get an ID
                person_id = None
            return True, person_id
    return False, None


def send_sms(message_text, distro_list):
    """Send Twilio SMS Message

    Args:
        message_text (str): The body of the message
        distro_list (list): a list of strings of phone numbers in the format
                            +15552229999

    Returns:
        twilio object: information about the message status after sending.
    """
    account_sid = st.secrets["twilio"]["account_sid"]
    auth_token = st.secrets["twilio"]["auth_token"]

    client = Client(account_sid, auth_token)

    for number in distro_list:
        message = client.messages.create(
            from_="+18449891781", body=message_text, to=number
        )

    return message.sid


def get_ld_context():
    """Creates and returns a LaunchDarkly context for the current user.
    
    Retrieves user information from the session state and builds a LaunchDarkly
    context object that can be used for feature flag evaluation. The context
    includes the user's key, name, and email.
    
    Returns:
        ldclient.Context: LaunchDarkly context object for the current user
    """
    # Get the LaunchDarkly SDK key from Streamlit Secrets
    sdk_key = st.secrets["other"]["launchdarkly_sdk_key"]
    ldclient.set_config(Config(sdk_key))

    # Get the user's information from Streamlit Authenticator
    app_username = st.session_state.username
    user_email = st.session_state.email
    user_name = st.session_state.name
    user_key = st.session_state["config"]["credentials"]["usernames"][app_username][
        "id"
    ]

    # Build the user context for LaunchDarkly
    builder = Context.builder(user_key)
    builder.kind("user")
    builder.name(user_name)
    builder.set("email", user_email)
    context = builder.build()

    return context


def mp_track_page_view(page_name):
    """Track a page view event in Mixpanel.
    
    Sends a page view event to Mixpanel with the current user's username
    and the name of the page being viewed. This function is called when
    a user navigates to a new page in the Deadpool application.
    """
    
    # initialize Mixpanel
    mp = Mixpanel(st.secrets["other"]["mixpanel"])
 
    mp.track(
        st.session_state["config"]["credentials"]["usernames"][
            st.session_state.username
        ]["id"],
        "Page View",
        {"Page": page_name, "User": st.session_state.username},
    )

    mp.people_set(
        st.session_state["config"]["credentials"]["usernames"][
            st.session_state.username
        ]["id"],
        {
            "name": st.session_state.name,
            "$email": st.session_state.email,
        },
    )
