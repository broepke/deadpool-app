import streamlit as st
from Home import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

conn = st.connection("snowflake")

df = conn.query(
    """select
        concat(first_name || ' ' || left(last_name, 1) || '.') as PLAYER, EMAIL 
    from PLAYERS
    order by 1
    """,
    ttl=600,
)

players = df["PLAYER"].tolist()

st.title("New User Registration")
with st.form("Registration"):
    first_name = st.text_input("Please Enter Your First Name:", "", 256, key="reg_first_name")
    last_name = st.text_input("Please Enter Your Last Name:", "", 256, key="reg_last_name")
    email = st.text_input("Please Enter Your Email:", "", 256, key="reg_email")
    sms = st.text_input("Please Enter Your Mobile Number:", "", 256, key="reg_sms")
    opt_in = st.checkbox("Opt-In to Receive SMS Alerts", True, key="reg_opt_in")
    
    email = email.lower()

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(first_name)
        st.write(last_name)
        st.write(email)
        st.write(sms)
        st.write(opt_in)
        
        # Check the DF to see if the user has already registered
        
        
        # Write the new user into the database
        # write_query = f"INSERT INTO players (name, email) VALUES ('{pick}', '{email}')"

        # conn.cursor().execute(write_query)