import streamlit as st
from hashlib import hash
from utilities import check_password, get_user_name, random_number_from_email

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except:
    st.write("Please login again")

conn = st.connection("snowflake")


def load_picks_table(table):
    session_picks = conn.session()
    return session_picks.table(table).to_pandas()


df = load_picks_table("players")

# get a list of all emails for checking for duplicates
all_emails = df["EMAIL"].tolist()

# get last year's max draft value - to increment
max_value = df["YEAR_ONE"].max()

st.title("New User Registration")
with st.form("Registration"):
    first_name = st.text_input(
        "Please Enter Your First Name:", "", 256, key="reg_first_name"
    )
    last_name = st.text_input(
        "Please Enter Your Last Name:", "", 256, key="reg_last_name"
    )
    email = st.text_input("Please Enter Your Personal Email:", "", 256, key="reg_email")
    sms = st.text_input("Please Enter Your Mobile Number Like This +12224446666:", "", 256, key="reg_sms")
    opt_in = st.checkbox("Opt-In to Receive SMS Alerts", True, key="reg_opt_in")

    email = email.lower()

    submitted = st.form_submit_button("Submit")
    if submitted:
        year_one = int(max_value) + 1
        
        random_num = round(random_number_from_email(email), 3)

        st.write(first_name)
        st.write(last_name)
        st.write(email)
        st.write(year_one)
        st.write(sms)
        st.write(opt_in)

        if email not in all_emails:
            # Write the new user into the database
            write_query = "INSERT INTO players (first_name, last_name, email, year_one, sms, opt_in, random_number) VALUES (:1, :2, :3, :4, :5, :6, :7)"

            # Execute the query with parameters
            conn.cursor().execute(
                write_query, (first_name, last_name, email, year_one, sms, opt_in, random_num)
            )
        else:
            st.write("User is already in the database.")
