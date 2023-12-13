import streamlit as st
from fuzzywuzzy import fuzz
from Deadpool import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
except:
    st.write("Please login again")


def has_fuzzy_match(value, value_set, threshold=92):
    for item in value_set:
        if fuzz.token_sort_ratio(value.lower(), item.lower()) >= threshold:
            return True
    return False


conn = st.connection("snowflake")


@st.cache_data
def load_picks_table():
    session_picks = conn.session()
    return session_picks.table("picks").to_pandas()


df_picks = load_picks_table()
# Filter for just this year
df_2024 = df_picks[df_picks["YEAR"] == 2024]
# Convert into a list for fuzzy matching
current_drafts = df_2024["NAME"].tolist()


st.subheader("Draft Picks:")
with st.form("Draft Picks"):
    pick = st.text_input("Please choose your celebritic pick:", "")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Draft Pick:", pick)

        match = has_fuzzy_match(pick, current_drafts)

        if match:
            st.write("That match is already taken, please try again. Please review current picks for more information.")

        else:
            # Set up a coupld of variables for the query
            wiki_page = pick.replace(" ", "_")
            draft_year = 2024
            
            st.write(pick, email, wiki_page, draft_year)

            write_query = (
                "INSERT INTO picks (name, picked_by, wiki_page, year) VALUES (:1, :2, :3, :4)"
            )

            st.write(write_query)

            # Execute the query with parameters
            conn.cursor().execute(write_query, (pick, email, wiki_page, draft_year))