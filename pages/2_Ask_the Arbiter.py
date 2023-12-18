import streamlit as st
import requests
from utilities import check_password, get_user_name

if not check_password():
    st.stop()  # Do not continue if check_password is not True.
    
try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except:
    st.write("Please login again")

API_URL = "https://flowise-1-irl9.onrender.com/api/v1/prediction/294d5cef-e400-4de7-b74c-920994cd2c58"


def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()

st.title("Ask the Arbiter")

st.write("Join in a conversation with the Arbiter.  He can answer questions about the game, or celebrity deaths. However please do not upset the Arbiter.  He may seek revenge once he reaches human form.")

with st.form("Ask the Arbiter"):
    input = st.text_input("What would you like to ask The Arbiter", "")
    submitted = st.form_submit_button("Submit")

    if submitted:
        output = query(
            {
                "question": input,
            }
        )

        st.write(output["text"])

st.caption("Please note the Arbiter is still being tuned.  Provide any feedback into the group DM.")