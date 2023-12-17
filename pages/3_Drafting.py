import streamlit as st
from fuzzywuzzy import fuzz
from Home import check_password
from twilio.rest import Client

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
except:
    st.write("Please login again")


def has_fuzzy_match(value, value_set, threshold=85):
    for item in value_set:
        if fuzz.token_sort_ratio(value.lower(), item.lower()) >= threshold:
            return True
    return False


def send_sms(message_text):
    account_sid = st.secrets["twilio"]["account_sid"]
    auth_token = st.secrets["twilio"]["auth_token"]

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_="+18449891781", body=message_text, to="+14155479222"
    )

    return message.sid


def draft_logic(email):
    # TODO: Draft logic
    # there is a list of players with a natural sort order
    # each player gets a pick.  The person that picks next will have the least number of picks
    # and the highest order

    # Get the table for the draft order
    df_draft = load_picks_table("draft")

    st.dataframe(df_draft)

    return True


conn = st.connection("snowflake")


def load_picks_table(table):
    session_picks = conn.session()
    return session_picks.table(table).to_pandas()


df_picks = load_picks_table("picks")
# Filter for just this year
df_2024 = df_picks[df_picks["YEAR"] == 2024]
# Convert into a list for fuzzy matching
current_drafts = df_2024["NAME"].tolist()

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

                st.write(pick, email, wiki_page, draft_year)

                write_query = "INSERT INTO picks (name, picked_by, wiki_page, year) VALUES (:1, :2, :3, :4)"

                st.write(write_query)

                # Execute the query with parameters
                conn.cursor().execute(write_query, (pick, email, wiki_page, draft_year))

                send_sms(email + " has picked " + pick)
