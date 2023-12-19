import streamlit as st
from datetime import datetime
from utilities import check_password, get_user_name, has_fuzzy_match, send_sms


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except:
    st.write("Please login again")


def draft_logic(email):
    # Get the table for the draft order
    df_draft = load_picks_table("draft_next")

    next_user = df_draft["EMAIL"].iloc[0]

    if email == next_user:
        return True
    else:
        st.write("It is not your turn. Please come back when it is.")
        return False


conn = st.connection("snowflake")


def load_picks_table(table):
    session_picks = conn.session()
    return session_picks.table(table).to_pandas()


df_picks = load_picks_table("picks")
# Filter for just this year
df_2024 = df_picks[df_picks["YEAR"] == 2024]
# Convert into a list for fuzzy matching
current_drafts = df_2024["NAME"].tolist()

# Get a list of the people that opted into alerts
df_opted = load_picks_table("draft_opted_in")
# Filter for just this year
# Convert into a list for fuzzy matching
opted_in_numbers = df_opted["SMS"].tolist()

# Only allow this to be show and run if not their turn.
if draft_logic(email):
    st.subheader("Draft Picks:")
    with st.form("Draft Picks"):
        pick = st.text_input("Please choose your celebrity pick:", "")

        pick = pick.strip()

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Draft Pick:", pick)

            match = has_fuzzy_match(pick, current_drafts)

            if match:
                st.write(
                    """That pick has already been taken, please try again. Please review the "All Picks" page for more information."""
                )

            else:
                # Set up a coupld of variables for the query
                wiki_page = pick.replace(" ", "_")
                draft_year = 2024
                timestamp = datetime.utcnow()

                write_query = "INSERT INTO picks (name, picked_by, wiki_page, year, timestamp) VALUES (:1, :2, :3, :4, :5)"

                # Execute the query with parameters
                conn.cursor().execute(write_query, (pick, email, wiki_page, draft_year, timestamp))

                sms_message = user_name + " has picked " + pick
                send_sms(sms_message, opted_in_numbers)

                df_next_sms = load_picks_table("draft_next")

                next_email = df_next_sms["EMAIL"].iloc[0]
                next_sms = df_next_sms["SMS"].iloc[0]

                next_sms_message = (
                    user_name
                    + """ is next to pick.  Please log into the website at https://deadpool.streamlit.app/Drafting to make your selection."""
                )
                send_sms(next_sms_message, [next_sms])

                st.rerun()


st.divider()

st.subheader("Tip for better pick entry")

st.markdown(
    """For the best results, use the same spelling of the person from their Wikipedia page. For example, Chris Burke was chosen in the past, his Wiki page's title is **"Chris Burke (actor)"** - if you enter this, it will speed up the disambiguation of the pick. Not critical but the arbiter will appreciate it."""
)

st.image("wiki.png", "Wikipedia Page Naming Convention")
