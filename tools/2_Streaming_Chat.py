from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

client = OpenAI()

# Create an expander for viewing the messages (debug)
view_messages = st.expander("View the message contents in session state")

# Initialize the mssage list if nedded
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render any messages in memory.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Draw the messages at the end, so newly generated ones show up immediately
    with view_messages:
        view_messages.json(st.session_state.messages)
