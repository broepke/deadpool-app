"""
Unified Drafting Page
"""

from datetime import datetime
import uuid
import streamlit as st
from dp_utilities import (
    has_fuzzy_match,
    send_sms,
    load_snowflake_table,
    snowflake_connection_helper,
    is_admin,
    mp_track_page_view,
)

PAGE_TITLE = "Drafting"
PAGE_ICON = ":skull:"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)


def submitted():
    st.session_state.submitted = True


def reset():
    st.session_state.submitted = False


def draft_logic(current_email):
    """Check to see if the current user is the person who will draft next

    Args:
        email (str): email of the current logged in person

    Returns:
        bool: If the person should draft or not
        str: Next user's ID
    """
    df_draft = load_snowflake_table(conn, "draft_next")
    try:
        next_user = df_draft["EMAIL"].iloc[0]
        next_user_id = df_draft["ID"].iloc[0]
        if current_email == next_user:
            return True, next_user_id

        st.write("It is not your turn. Please come back when it is.")
        return False, ""
    except IndexError:
        st.write("And with that the 2024 Draft is over!")
        return False, ""


def draft_pick(pick, user_info, conn, opted_in_numbers, admin_mode=False):
    """Handles the draft logic for both regular users and admins"""
    try:
        if not pick:
            st.write("Please enter a valid selection.")
            return

        MATCH = has_fuzzy_match(pick, current_drafts)
        if MATCH:
            st.write("That pick has already been taken. Please try again.")
            return

        new_id = uuid.uuid4()
        wiki_page = pick.replace(" ", "_")
        DRAFT_YEAR = datetime.now().year
        timestamp = datetime.now(datetime.timezone.utc)

        WRITE_PEOPLE_QUERY = """
        INSERT INTO people (id, name, wiki_page)
        VALUES (%s, %s, %s)
        """
        conn.cursor().execute(WRITE_PEOPLE_QUERY, (new_id, pick, wiki_page))

        WRITE_PLAYER_PICKS_QUERY = """
        INSERT INTO player_picks (player_id, year, people_id, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        next_user_id = user_info["ID"].iloc[0] if admin_mode else user_info
        conn.cursor().execute(
            WRITE_PLAYER_PICKS_QUERY, (next_user_id, DRAFT_YEAR, new_id, timestamp)
        )

        st.caption("Draft pick complete")
        send_sms(f"{user_name} has picked {pick}", opted_in_numbers)

        df_next_sms = load_snowflake_table(conn, "draft_next")
        if not df_next_sms.empty:
            next_name = df_next_sms["NAME"].iloc[0]
            next_sms = df_next_sms["SMS"].iloc[0]
            next_sms_message = (
                f"{next_name} is next to pick. Please log in to the website."
            )
            send_sms(next_sms_message, [next_sms])
    except Exception as e:
        st.write(f"Error occurred: {e}")


st.title("Drafting :skull_and_crossbones:")

if st.session_state.get("authentication_status") is not None:
    authenticator = st.session_state.get("authenticator")
    authenticator.logout(location="sidebar", key="deadpool-app-logout-drafting")
    authenticator.login(location="unrendered", key="deadpool-app-login-drafting")
    
    mp_track_page_view(PAGE_TITLE)
    
    name = st.session_state.name
    email = st.session_state.email
    user_name = st.session_state.username
    st.sidebar.write(f"Welcome, {name}")
    st.sidebar.write(f"Email: {email}")

    conn = snowflake_connection_helper()
    df_picks = load_snowflake_table(conn, "picks_current_year")
    current_drafts = df_picks["NAME"].tolist()
    df_opted = load_snowflake_table(conn, "draft_opted_in")
    opted_in_numbers = df_opted["SMS"].tolist()

    if is_admin():
        st.write("Admin Mode Enabled")
        df_players = load_snowflake_table(conn, "draft_next")
        try:
            df_player = df_players["EMAIL"].iloc[0]
            st.write("Drafting for:", df_player)
            with st.form("Draft Picks"):
                pick = st.text_input(
                    "Please choose the celebrity pick for the next player:",
                    "",
                    key="celeb_auto_pick",
                ).strip()

                if st.form_submit_button("Submit", on_click=submitted):
                    draft_pick(
                        pick, df_players, conn, opted_in_numbers, admin_mode=True
                    )
        except Exception as e:
            st.write("There are no additional players to draft for.")
            st.caption(f"Error: {str(e)}")
    else:
        st.write("Regular User Mode")
        is_next, next_user_id = draft_logic(email)
        if is_next:
            st.subheader("Draft Picks:")
            with st.form("Draft Picks"):
                pick = st.text_input(
                    "Please choose your celebrity pick:", "", key="celeb_pick"
                ).strip()

                if st.form_submit_button("Submit", on_click=submitted):
                    draft_pick(pick, email, conn, opted_in_numbers, admin_mode=False)
else:
    st.warning("Please use the button below to navigate to Home and log in.")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.stop()
