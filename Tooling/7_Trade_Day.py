"""
Main page for Trade Day
"""
from datetime import datetime
import streamlit as st
from dp_utilities import (
    check_password,
    has_fuzzy_match,
    send_sms,
    load_snowflake_table,
)

st.set_page_config(page_title="Trade Day", page_icon=":skull:")

st.title("Trade Day :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
    # Function to check if today is the first day of any calendar quarter
    def is_first_day_of_quarter(date):
        # Extract month and day from the date
        month = date.month
        day = date.day

        # Check if it's the first day of the quarter
        return (month in [1, 4, 7, 10]) and (day == 1)

    def draft_day():
        # Check if today is the first day of a quarter
        today = datetime.now()
        is_first_day_of_quarter_today = is_first_day_of_quarter(today)
        if is_first_day_of_quarter_today:
            return True
        else:
            st.write(
                "Trade Days are on the first day of the calendar quarter. "
                "Come back soon."
            )
            return False

    conn = st.connection("snowflake")

    # Get all the Picks for Fuzzy Matching
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

    # Get a list of all the people that are opted in for SMS and playing
    df_picks = load_snowflake_table(conn, "picks")
    df_picks_2024 = df_picks[
        (df_picks["YEAR"] == 2024) & (df_picks["PICKED_BY"] == email)
    ]
    df_picks_list = df_picks_2024["NAME"].to_list()
    df_picks_list.sort()

    # Only allow this to be show and run if not their turn.
    if draft_day():
        st.subheader("Trade Day:")
        with st.form("Trade Day"):
            sel_pick = st.selectbox(
                "Select a pick", df_picks_list, key="sel_selected_pick"
            )

            pick = st.text_input("Please choose your celebrity pick:", "")

            pick = pick.strip()

            submitted = st.form_submit_button("Submit")
            if submitted:
                st.write("Original Pick:", sel_pick)
                st.write("Trade Pick:", pick)

                MATCH = has_fuzzy_match(pick, current_drafts)

                if MATCH:
                    st.write(
                        """That pick has already been taken, please try again. Please review the "All Picks" page for more information."""  # noqa: E501
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
                        (pick, email, wiki_page, DRAFT_YEAR, timestamp),  # noqa: E501
                    )

                    DELETE_QUERY = "DELETE FROM picks WHERE name = :1 AND picked_by = :2 AND YEAR = :3"  # noqa: E501

                    # Execute the query with parameters
                    conn.cursor().execute(
                        DELETE_QUERY, (sel_pick, email, DRAFT_YEAR)
                    )  # noqa: E501

                    sms_message = user_name
                    +" has traded "
                    +sel_pick
                    +" for "
                    +pick

                    send_sms(sms_message, opted_in_numbers)

                    df_next_sms = load_snowflake_table(conn, "draft_next")

                    try:
                        next_name = df_next_sms["NAME"].iloc[0]
                        next_email = df_next_sms["EMAIL"].iloc[0]
                        next_sms = df_next_sms["SMS"].iloc[0]

                        # Send alert to the next player
                        next_sms_message = (
                            next_name
                            + """ is next to pick.  Please log into the website at https://deadpool.streamlit.app/Trade_Day to make your selection."""  # noqa: E501
                        )
                        send_sms(next_sms_message, [next_sms])
                    except IndexError:
                        st.write("No additional names")

                    st.rerun()
