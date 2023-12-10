import streamlit as st


# Initialize connection.
conn = st.connection("snowflake")


@st.cache_data
def load_players_table():
    session_players = conn.session()
    return session_players.table("players").to_pandas()


df_players = load_players_table()

# Add some text
st.title("Deadpool 2024 :skull_and_crossbones:")

st.subheader("Current Players:")
st.dataframe(df_players)


