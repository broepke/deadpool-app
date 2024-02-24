"""The Arbiter LLM Based Chatbot"""
import streamlit as st
from openai import OpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
# from dp_utilities import check_password


st.set_page_config(page_title="Ask the Arbiter", page_icon=":skull:")

st.title("Ask the Arbiter :skull_and_crossbones:")

client = OpenAI()

tool_names = ["pandas"]
tools = ["pandas"]

# Generate LLM response
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Arbiter.  You are the judge of the game DEADPOOL. You have access to a data frame with a column called NAME, which represents celebrity picks for this year, 2024.  The PLAYERS column contains the game's participants.  When asked about the score or points in the game, you should apply the following formula (50 + (100-AGE)).  Points only count when the NAME is dead as indicated by the DEATH_DATE column being not null.  When you calculate the leaders of the game, you must only count NAMES that have a DEATH_DATE and then calculate the points with the formula.  There is a special rule also that if during the course of the year, a players pick dies, they are awarded an additional pick such that all players have 20 picks that are alive at all times.  All of your judgments are final, and you should let the person asking the question know this. When you deal with these dataframes, please join them together by the ID field in PLAYERS and the PICKED_BY field in PICKS.",  # noqa: E501
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# openai_api_key = st.secrets["llm"]["openai_api_key"]


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
response = chain_with_history.invoke({"input": user_prompt, "tools": tools, "tool_names": tool_names}, config)  # noqa: E501




# Get the snowflake connection
conn = st.connection("snowflake")


# Cache the snowflake table for an hour.  It's pretty static.
@st.cache_data(ttl=3600)
def get_snowflake_table(_conn, table_name):
    snowflake_table = _conn.session()
    return snowflake_table.table(table_name).to_pandas()


# Create an expander for viewing the messages (debug)
view_messages = st.expander("View the message contents in session state")

# Initialize the mssage list if nedded
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render any messages in memory.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Fetch the Players table
df_players = get_snowflake_table(conn, "players")

# Fetch the Picks table and filter
df2 = get_snowflake_table(conn, "picks")
df_picks = df2[df2["YEAR"] == 2024]


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
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
