"""The Arbiter LLM Based Chatbot"""
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)  # noqa: E501
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from dp_utilities import check_password


st.set_page_config(page_title="Ask the Arbiter", page_icon=":skull:")

st.title("Ask the Arbiter :skull_and_crossbones:")


def fetch_llm_results(df, user_prompt):
    # Generate LLM response
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the Arbiter.  You are the judge of the game DEADPOOL. You have access to a data frame with a column called NAME, which represents celebrity picks for this year, 2024.  The PLAYERS column contains the game's participants.  When asked about the score or points in the game, you should apply the following formula (50 + (100-AGE)).  Points only count when the NAME is dead as indicated by the DEATH_DATE column being not null.  When you calculate the leaders of the game, you must only count NAMES that have a DEATH_DATE and then calculate the points with the formula.  All of your judgments are final, and you should let the person asking the question know this.",  # noqa: E501
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    openai_api_key = st.secrets["llm"]["openai_api_key"]

    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0.9,
        openai_api_key=openai_api_key,
        streaming=True,  # noqa: E501
    )

    # Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        agent_executor_kwargs={"handle_parsing_errors": True},
    )

    chain = prompt | agent

    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: msgs,
        input_messages_key="input",
        history_messages_key="history",
    )

    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"input": user_prompt}, config)

    return response


# Get the snowflake connection
conn = st.connection("snowflake")


@st.cache_data(ttl=3600)
def get_snowflake_table(_conn, table_name):
    snowflake_table = _conn.session()
    return snowflake_table.table(table_name).to_pandas()


view_messages = st.expander("View the message contents in session state")


email, user_name, authticated = check_password()
if authticated:
    # Set up memory
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    if len(msgs.messages) == 0:
        msgs.add_ai_message("What questions do you have about the Deadpool?")

    # Render current messages from StreamlitChatMessageHistory
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)

    # Fetch the table
    df = get_snowflake_table(conn, "picks_twenty_four")

    # If user inputs a new prompt, generate and draw a new response
    if prompt := st.chat_input():
        # Write and save the human message
        with st.chat_message("human"):
            st.write(prompt)
            # Note: new messages are saved to history
            # automatically by Langchain
            response = fetch_llm_results(df=df, user_prompt=prompt)

        # Write and save the AI message
        with st.chat_message("ai"):
            st.write(response["output"])


# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Message History initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)
