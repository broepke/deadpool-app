"""
Main page for Drafting new picks
"""
from datetime import datetime
import streamlit as st
from dp_utilities import has_fuzzy_match, send_sms, load_snowflake_table
from dp_utilities import check_password

st.set_page_config(page_title="Drafting", page_icon=":skull:")


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
    # Get the table for the draft order
    df_draft = load_snowflake_table(conn, "draft_next")

    # Handle the condition when the table is empty
    try:
        next_user = df_draft["EMAIL"].iloc[0]
        next_user_id = df_draft["ID"].iloc[0]
        if current_email == next_user:
            return True, next_user_id

        st.write("It is not your turn. Please come back when it is.")
        return False, ""
    except IndexError:
        # Send out SMS and write to page.
        st.write("And with that the 2024 Draft is over!")
        return False, ""


st.title("Drafting :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
    conn = st.connection("snowflake")

    df_picks = load_snowflake_table(conn, "picks")
    # Filter for just this year
    df_2024 = df_picks[df_picks["YEAR"] == 2024]
    # Convert into a list for fuzzy matching
    current_drafts = df_2024["NAME"].tolist()

    # Get a list of the people that opted into alerts
    df_opted = load_snowflake_table(conn, "draft_opted_in")
    # Filter for just this year
    # Convert into a list for fuzzy matching
    opted_in_numbers = df_opted["SMS"].tolist()

    st.write("Current User:", email)

    # Only allow this to be show and run if not their turn.
    is_next, next_user_id = draft_logic(email)
    if is_next:
        st.subheader("Draft Picks:")
        with st.form("Draft Picks"):
            pick = st.text_input(
                "Please choose your celebrity pick:", "", key="celeb_pick"
            )

            pick = pick.strip()

            st.form_submit_button("Submit", on_click=submitted)

# See: https://discuss.streamlit.io/t/submit-form-button-not-working/35059/2
if "submitted" in st.session_state:
    if st.session_state.submitted:
        st.write("Draft Pick:", pick)

        MATCH = has_fuzzy_match(pick, current_drafts)

        if MATCH:
            st.write(
                """That pick has already been taken, please try again. Please review the "Draft Picks" page for more information."""  # noqa: E501
            )

        else:
            # Set up a coupld of variables for the query
            wiki_page = pick.replace(" ", "_")
            DRAFT_YEAR = 2024
            timestamp = datetime.utcnow()

            WRITE_QUERY = "INSERT INTO picks (name, picked_by, wiki_page, year, timestamp) VALUES (:1, :2, :3, :4, :5)"  # noqa: E501

            # Execute the query with parameters
            conn.cursor().execute(
                WRITE_QUERY,
                (pick, next_user_id, wiki_page, DRAFT_YEAR, timestamp),
            )

            st.caption("Datebase query executed")
            st.caption(
                pick
                + ", "
                + next_user_id
                + ", "
                + wiki_page
                + ", "
                + str(DRAFT_YEAR)
                + ", "
                + str(timestamp)
            )

            sms_message = user_name + " has picked " + pick
            send_sms(sms_message, opted_in_numbers)

            df_next_sms = load_snowflake_table(conn, "draft_next")

            try:
                next_name = df_next_sms["NAME"].iloc[0]
                next_email = df_next_sms["EMAIL"].iloc[0]
                next_sms = df_next_sms["SMS"].iloc[0]

                # Send alert to the next player
                next_sms_message = (
                    next_name
                    + """ is next to pick.  Please log into the website at https://deadpool.streamlit.app/Drafting to make your selection."""  # noqa: E501
                )
                send_sms(next_sms_message, [next_sms])

                st.caption("SMS messages sent")

            except IndexError:
                st.write("No additional names")

        st.caption("Draft pick complete")

        reset()

    st.divider()

    st.markdown(
        """
    **Notes**:
    - The system checks for duplicate entries and has built-in fuzzy matching of names entered.  If it's a slight misspelling, the duplicate will be caught.  If it's way off, the Arbiter must de-duplicate and resolve it after draft day.  The person with the earlier timestamp on the pick will keep the pick.  The other person will get to submit an additional pick.
    - Please do not pick a dead person.  If you do, you will lose that pick and receive 0 points.
    """  # noqa: E501
    )
