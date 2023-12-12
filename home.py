"""
Streamlit main app
"""
import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Initialize connection.
conn = st.connection("snowflake")


@st.cache_data
def load_players_table():
    session_players = conn.session()
    return session_players.table("players").to_pandas()


df_players = load_players_table()

# Add some text
st.title("Deadpool 2024 :skull_and_crossbones:")

st.image("deadpool.png", "Deadpool 2024")

st.subheader("Current Players:")
st.dataframe(df_players)


