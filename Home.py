"""
Streamlit main app
"""
import hmac
import streamlit as st


def save_value(key):
    st.session_state[key] = st.session_state["_" + key]


# I'm not sure if this will be needed
def get_value(key):
    st.session_state["_" + key] = st.session_state[key]


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="_username")
            st.text_input("Password", type="password", key="_password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["_username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["_password"],
            st.secrets.passwords[st.session_state["_username"]],
        ):
            st.session_state["password_correct"] = True
            save_value("username")
            del st.session_state["_password"]  # Don't store the username or password.
            del st.session_state["_username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


# Add some text
st.title("Deadpool 2024 :skull_and_crossbones:")

st.write("Current User: " + st.session_state["username"])

st.markdown(
    """
Welcome to **Deadpool 2024**, the annual fantasy draft where every pick you make has you cheering for a famous person's death! Deadpool is not just a game; it's a journey into the degenerate behavior that you've been known for. Feel the excitement build as you assemble your dream (death) team, strategizing against rivals in a quest for glory. Here, every round is a spectacle; every decision echoes with the crowd's roar. **Deadpool 2024** is more than fantasy; it's where celebrity death enthusiasts become architects of their destiny. Get ready to experience the exhilaration of victory and the rush of competition like never before. Buckle up, and let the games begin!
           """
)

st.image("deadpool.png", "The Arbiter")
