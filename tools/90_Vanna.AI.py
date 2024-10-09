from vanna.remote import VannaDefault
import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def setup_session_state():
    st.session_state["my_question"] = None


api_key = st.secrets["llm"]["vanna_api_key"]

vanna_model_name = "deadpool-test"
vn = VannaDefault(model=vanna_model_name, api_key=api_key)

SNOW_ACCOUNT = st.secrets["connections"]["snowflake"]["account"]
SNOW_USER = st.secrets["connections"]["snowflake"]["user"]
SNOW_KEY = st.secrets["connections"]["snowflake"]["private_key"]
SNOW_WAREHOUSE = "DEADPOOL"
SNOW_DATABASE = "DEADPOOL"




# Function to load the private key from secrets
def load_private_key_from_secrets(private_key_str):
    private_key = serialization.load_pem_private_key(
        private_key_str.encode(),  # Convert the string to bytes
        password=None,
        backend=default_backend(),
    )
    return private_key


private_key = load_private_key_from_secrets(SNOW_KEY)

vn.connect_to_snowflake(
    account=SNOW_ACCOUNT,
    username=SNOW_USER,
    private_key=private_key,
    database=SNOW_DATABASE,
    role="ENGINEER",
)

st.sidebar.button("Rerun", on_click=setup_session_state, use_container_width=True)

st.title("Vanna.AI")


def set_question(question):
    st.session_state["my_question"] = question


my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "Ask me a question about your data",
    )


if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    if my_question is not None:
        assistant_message_table = st.chat_message("assistant")

        sql = vn.generate_sql(question=my_question)
        answer = vn.run_sql(sql)

        assistant_message_table.code(sql)
        assistant_message_table.write(answer)

    else:
        assistant_message_error = st.chat_message("assistant")
        assistant_message_error.error("I wasn't able to generate SQL.")
        st.write(st.session_state)
