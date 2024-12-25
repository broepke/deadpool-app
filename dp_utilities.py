"""
Reusable components
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
    """Simple methods for setting temp and permanent session state keys"""
    st.session_state[key] = st.session_state["_" + key]


def load_snowflake_table(_conn, table):
    """Loads a specific Snowflake table using SQL

    Args:
        _conn (conn): Snowflake connection
        table (str): table or view - no DB or schema needed

    Returns:
        DataFrame: dataframe of the entire table.
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
    with _conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetch_pandas_all()
        return result


def is_admin():
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
    """Chatbot API call to LangChang LLM

    Args:
        prompt (str): the prompt

    Returns:
        str: Text output from the LLM
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
    """NLP based text maching

    Args:
        value (str): value to check
        df (DataFrame): DF of all values you want to compare against
        column (str): column in the DF to compare against
        threshold (int, optional): how much leway do you want to give the
        algoritm. Defaults to 85.

    Returns:
        bool: if there is a match or not
    """
    
    value_set = df[column].tolist()
    
    for index, item in enumerate(value_set):
        if fuzz.token_sort_ratio(value.lower(), item.lower()) >= threshold:
            person_id = df.iloc[index]["ID"]
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