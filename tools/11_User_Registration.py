"""
New User Registration
"""

from uuid import uuid4
import streamlit as st
from dp_utilities import (
    check_password,
    get_user_name,
    load_snowflake_table,
)

st.set_page_config(page_title="User Registration", page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except KeyError:
    st.write("Please login again")

conn = st.connection("snowflake")


df = load_snowflake_table(conn, "players")

# get a list of all emails for checking for duplicates
all_emails = df["EMAIL"].tolist()

st.title("New User Registration")
with st.form("Registration"):
    first_name = st.text_input(
        "Please Enter Your First Name:", "", 256, key="reg_first_name"
    )
    last_name = st.text_input(
        "Please Enter Your Last Name:", "", 256, key="reg_last_name"
    )
    email = st.text_input("Please Enter Your Personal Email:", "", 256, key="reg_email")
    sms = st.text_input("Please Enter Your Mobile Number:", "", 256, key="reg_sms")
    opt_in = st.checkbox("Opt-In to Receive SMS Alerts", True, key="reg_opt_in")

    email = email.lower()

    submitted = st.form_submit_button("Submit")
    if submitted:
        ID = str(uuid4())
        YEAR_ONE = 0

        st.write(ID)
        st.write(first_name)
        st.write(last_name)
        st.write(email)
        st.write(YEAR_ONE)
        st.write(sms)
        st.write(opt_in)

        if email not in all_emails:
            # Write the new user into the database
            WRITE_QUERY = """INSERT INTO players (FIRST_NAME, LAST_NAME, EMAIL, YEAR_ONE, SMS, OPT_IN, ID) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            # Execute the query with parameters
            conn.cursor().execute(
                WRITE_QUERY,
                (first_name, last_name, email, YEAR_ONE, sms, opt_in, ID),
            )
        else:
            st.write("User is already in the database.")
