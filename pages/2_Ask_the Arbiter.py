"""The Arbiter LLM Based Chatbot"""
import time
import streamlit as st
from ..dp_utilities import check_password, the_arbiter

st.set_page_config(page_title="Ask the Arbiter", page_icon=":skull:")

st.title("Ask the Arbiter :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
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

    st.caption(
        "If you don't like a response please enter: 'I would like to speak to a manager' along with your complaint"  # noqa: E501
        )
