"""
Reusable components
"""
import hmac
import requests
import random
import hashlib
from fuzzywuzzy import fuzz
from twilio.rest import Client
import streamlit as st


def save_value(key):
    st.session_state[key] = st.session_state["_" + key]

def load_snowflake_table(conn, table):
    """Loads a specific Snowflake table

    Args:
        conn (conn): st.connection
        table (str): table or view - no DB or schema needed

    Returns:
        DataFrame: dataframe of the entire table.
    """
    session_picks = conn.session()
    return session_picks.table(table).to_pandas()

def get_user_name(email):
    conn = st.connection("snowflake")

    df_players = load_snowflake_table(conn, "players")
    filtered_df = df_players[df_players["EMAIL"] == email]
    first_name = filtered_df.iloc[0]["FIRST_NAME"]
    last_name = filtered_df.iloc[0]["LAST_NAME"]

    users_full_name = first_name + " " + last_name

    st.session_state.users_full_name = users_full_name

    return users_full_name


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="_username")
            st.text_input("Password", type="password", key="_password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["_username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["_password"],
            st.secrets.passwords[st.session_state["_username"]],
        ):
            st.session_state["password_correct"] = True
            save_value("username")
            del st.session_state["_password"]  # Don't store the username or password.
            del st.session_state["_username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


def the_arbiter(prompt):
    """Chatbot API call to LangChang LLM

    Args:
        payload (dict): output = the_arbiter(
            {"question": input,}
            )

    Returns:
        str: Text output from the LLM
    """
    API_URL = st.secrets["apify"]["api_url"]
    response = requests.post(API_URL, json=prompt)
    return response.json()


def has_fuzzy_match(value, value_set, threshold=85):
    """NLP based text maching

    Args:
        value (str): value to check
        value_set (list, str): list of all values you want to compare against
        threshold (int, optional): how much leway do you want to give the algoritm.
        Defaults to 85.

    Returns:
        _type_: _description_
    """
    for item in value_set:
        if fuzz.token_sort_ratio(value.lower(), item.lower()) >= threshold:
            return True
    return False


def send_sms(message_text, distro_list):
    account_sid = st.secrets["twilio"]["account_sid"]
    auth_token = st.secrets["twilio"]["auth_token"]

    client = Client(account_sid, auth_token)

    for number in distro_list:
        message = client.messages.create(
            from_="+18449891781", body=message_text, to=number
        )

    return message.sid


def random_number_from_email(email):
    """Hashes an email address using SHA-256."""

    email_hash = int(hashlib.sha256(email.encode()).hexdigest(), 16)
    # Set the seed
    random.seed(email_hash)

    return random.random()