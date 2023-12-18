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


def send_sms(message_text, distro_list):
    account_sid = st.secrets["twilio"]["account_sid"]
    auth_token = st.secrets["twilio"]["auth_token"]

    client = Client(account_sid, auth_token)

    for number in distro_list:
        message = client.messages.create(
            from_="+18449891781", body=message_text, to=number
        )

    return message.sid


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
        
        st.write("""For the best results, use the same spelling of the person from their Wikipedia page. For example, Chris Burke was chosen in the past, his Wiki page's title is "Chris Burke (actor)" - if you enter this, it will speed up the disambiguation of the pick. Not critical but the arbiter will appreciate it.""")
        
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

                write_query = "INSERT INTO picks (name, picked_by, wiki_page, year) VALUES (:1, :2, :3, :4)"

                # Execute the query with parameters
                conn.cursor().execute(write_query, (pick, email, wiki_page, draft_year))

                sms_message = email + " has picked " + pick
                send_sms(sms_message, opted_in_numbers)

                df_next_sms = load_picks_table("draft_next")

                next_email = df_next_sms["EMAIL"].iloc[0]
                next_sms = df_next_sms["SMS"].iloc[0]

                next_sms_message = (
                    next_email
                    + """ is next to pick.  Please log into the website at https://deadpool.streamlit.app and go to the Drafting page to make your selection."""
                )
                send_sms(next_sms_message, [next_sms])

                st.rerun()
