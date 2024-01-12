"""
Reusable components
"""
import requests
from fuzzywuzzy import fuzz
from twilio.rest import Client
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def check_password():
    """Implementes:
    https://github.com/mkhorasani/Streamlit-Authenticator

    Returns:
        str: email address of user
        str: User's full name
        bool: If they've successfully authenticated
    """
    # Get all credentials
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    # --- Authentication Code
    authenticator.login("Login", "main")

    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return "", "", False
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")
        return "", "", False
    elif st.session_state["authentication_status"]:
        authenticator.logout("Logout", "sidebar", key="unique_key")
        user_name = st.session_state["name"]
        email = st.session_state["username"]
        st.sidebar.write(f"Welcome, {user_name}")
        st.sidebar.write(f"Email: {email}")

        return email, user_name, True


def save_value(key):
    """Simple methods for setting temp and permanent session state keys"""
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


def run_snowflake_query(conn, query):
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetch_pandas_all()
        return result


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


def has_fuzzy_match(value, value_set, threshold=85):
    """NLP based text maching

    Args:
        value (str): value to check
        value_set (list, str): list of all values you want to compare against
        threshold (int, optional): how much leway do you want to give the
        algoritm. Defaults to 85.

    Returns:
        bool: if there is a match or not
    """
    for item in value_set:
        if fuzz.token_sort_ratio(value.lower(), item.lower()) >= threshold:
            return True
    return False


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
