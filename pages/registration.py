import streamlit as st

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
    first_name = st.text_input("Please Enter Your First Name:", "")
    last_name = st.text_input("Please Enter Your Last Name:", "")
    email = st.text_input("Please Enter Your Email:", "")
    
    email = email.lower()

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(first_name)
        st.write(last_name)
        st.write(email)
        
        # Check the DF to see if the user has already registered
        
        
        # Write the new user into the database
        # write_query = f"INSERT INTO players (name, picked_by) VALUES ('{pick}', '{email}')"

        # conn.cursor().execute(write_query)