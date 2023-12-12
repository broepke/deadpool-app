import streamlit as st
from home import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


conn = st.connection("snowflake")

# df = conn.query(
#     """select
#         concat(first_name || ' ' || left(last_name, 1) || '.') as PLAYER, EMAIL
#     from PLAYERS
#     order by 1
#     """,
#     ttl=600,
# )

# players = df["PLAYER"].tolist()

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
except:
    st.write("Please login again")


st.subheader("Draft Picks:")
with st.form("Draft Picks"):
    pick = st.text_input("Please choose your celebritic pick:", "")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Draft Pick:", pick)
        
        wiki_page = pick.replace(" ", "_")

        write_query = (
            f"INSERT INTO picks (name, picked_by, wiki_page) VALUES ('{pick}', '{email}', '{wiki_page}')"
        )

        st.write(write_query)

        conn.cursor().execute(write_query)
