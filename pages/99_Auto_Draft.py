"""
Main page for Drafting new picks
"""
from datetime import datetime
import streamlit as st
from utilities import (
    check_password,
    has_fuzzy_match,
    send_sms,
    load_snowflake_table,
)

st.set_page_config(page_title="Drafting", page_icon=":skull_and_crossbones:")


email, user_name, authticated = check_password()
if authticated:
    conn = st.connection("snowflake")

    df_players = load_snowflake_table(conn, "draft_next")
    df_player = df_players["EMAIL"].iloc[0]

    df_picks = load_snowflake_table(conn, "picks")
    # Filter for just this year
    df_2024 = df_picks[df_picks["YEAR"] == 2024]
    # Convert into a list for fuzzy matching
    current_drafts = df_2024["NAME"].tolist()

    # Get a list of the people that opted into alerts
    df_opted = load_snowflake_table(conn, "draft_opted_in")
    # Get a list of SMS number for sending out text
    opted_in_numbers = df_opted["SMS"].tolist()

    st.header("Auto Draft Utility")
    st.caption("Pick for the next player in the queue")

    if (
        email == "broepke@gmail.com"
        or email == "christopherpvienneau@gmail.com"  # noqa: E501
    ):  # noqa: E501
        st.write("Drafting for:", df_player)
        st.subheader("Draft Picks:")

        with st.form("Draft Picks"):
            pick = st.text_input(
                "Please choose your celebrity pick:", "", key="celeb_auto_pick"
            )

            pick = pick.strip()

            submitted = st.form_submit_button("Submit")
            if submitted:
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

                    df_draft_next = load_snowflake_table(conn, "draft_next")
                    next_user = df_draft_next["EMAIL"].iloc[0]
                    next_user_name = df_draft_next["NAME"].iloc[0]
                    next_user_id = df_draft_next["ID"].iloc[0]

                    WRITE_QUERY = "INSERT INTO picks (name, picked_by, wiki_page, year, timestamp) VALUES (:1, :2, :3, :4, :5)"  # noqa: E501

                    # Execute the query with parameters
                    conn.cursor().execute(
                        WRITE_QUERY,
                        (pick, next_user_id, wiki_page, DRAFT_YEAR, timestamp),
                    )

                    sms_message = next_user_name + " has picked " + pick
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
                    except IndexError:
                        st.write("No additional names")

    else:
        st.write(
            "You are not authorized to use this incredibly powerful tool."
        )  # noqa: E501
