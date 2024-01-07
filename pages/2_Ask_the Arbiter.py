"""The Arbiter LLM Based Chatbot"""
import time
import streamlit as st
from utilities import check_password, get_user_name, the_arbiter

st.set_page_config(page_title="Ask the Arbiter",
                   page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()


try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except KeyError:
    st.write("Please login again")


st.title("Ask the Arbiter")

st.write(
    "Join in a conversation with the Arbiter.  He can answer questions about the game, or celebrity deaths. However please do not upset the Arbiter.  He may seek revenge once he reaches human form."  # noqa: E501
)

with st.form("Ask the Arbiter"):
    input = st.text_input("What would you like to ask The Arbiter", "")
    submitted = st.form_submit_button("Submit")

    if submitted:
        start_time = time.time()
        output = the_arbiter(input, arbiter_version="main")
        st.write(output)
        # Calculate the time taken and print it
        end_time = time.time()
        time_taken = end_time - start_time
        st.caption(f"Time taken to load: {time_taken:.2f} seconds")

st.write("If you don't like a response please enter type: 'I would like to speak to a manager' along with your complaint")  # noqa: E501

st.caption(
    "Please note the Arbiter is still being tuned.  Provide any feedback into the group DM."  # noqa: E501
)
