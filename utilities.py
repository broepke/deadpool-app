"""
Reusable components
"""
import hmac
import streamlit as st


def save_value(key):
    st.session_state[key] = st.session_state["_" + key]


def get_user_name(email):
    conn = st.connection("snowflake")

    @st.cache_data
    def load_score_table(table):
        session_score = conn.session()
        return session_score.table(table).to_pandas()

    df_players = load_score_table("players")
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
