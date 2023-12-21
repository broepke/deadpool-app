"""
User maintenance tools
"""
import streamlit as st
from utilities import check_password, get_user_name, load_snowflake_table

st.set_page_config(page_title="User Maintenance", page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except KeyError:
    st.write("Please login again")


st.title("User Maintenance Tools")
st.markdown(
    """
Use this form to adjust any personal information you need.  The email is the key information here, and if you so choose to opt in to SMS messaging you can do so below.  If you opt out, you will not receive pick or death alerts.  It is highly reccomended that you opt in!
1. Select your name and click "Choose Player."
2. Adjust any information as needed.
3. Click "Submit".  

If for any reason you see an error, please contact the Arbiter.
"""  # noqa: E501
)

# Initialize important varibles
SEL_FIRST_NAME = ""
SEL_LAST_NAME = ""
SEL_EMAIL = ""
SEL_SMS = ""
SEL_OPT_IN = True

# Initialize connection.
conn = st.connection("snowflake")


df_players = load_snowflake_table(conn, "players")
df_players_list = df_players["EMAIL"].to_list()

st.header("Player Selection")

# Load all the players into a drop down for easy selection
with st.form("Player to Update"):
    sel_player = st.selectbox(
        "Select a Player", df_players_list, key="sel_selected_player"
    )
    submitted = st.form_submit_button("Choose Player")

    if submitted:
        filtered_df = df_players[df_players["EMAIL"] == sel_player]

        if not filtered_df.empty:
            SEL_FIRST_NAME = filtered_df.iloc[0]["FIRST_NAME"]
            SEL_LAST_NAME = filtered_df.iloc[0]["LAST_NAME"]
            SEL_EMAIL = filtered_df.iloc[0]["EMAIL"]
            SEL_SMS = filtered_df.iloc[0]["SMS"]
            SEL_OPT_IN = filtered_df.iloc[0]["OPT_IN"]

            st.session_state["reg_first_name"] = SEL_FIRST_NAME
            st.session_state["reg_last_name"] = SEL_LAST_NAME
            st.session_state["reg_email"] = SEL_EMAIL
            st.session_state["reg_sms"] = SEL_SMS
            st.session_state["reg_opt_in"] = SEL_OPT_IN
            st.session_state["reg_player"] = SEL_EMAIL

        else:
            print("No user found with the given email")

st.header("Update Player Information")
st.write("Note: Your cannot update the email address.  Please contact The Aribiter")

with st.form("Registration"):
    try:
        SEL_FIRST_NAME = st.session_state["reg_first_name"]
        SEL_LAST_NAME = st.session_state["reg_last_name"]
        SEL_EMAIL = st.session_state["reg_email"]
        SEL_OPT_IN = st.session_state["reg_opt_in"]
        SEL_SMS = st.session_state["reg_sms"]
        SUB_PLAYER = st.session_state["reg_player"]
    except KeyError:
        SEL_FIRST_NAME = ""
        SEL_LAST_NAME = ""
        SEL_EMAIL = ""
        SEL_OPT_IN = ""
        SEL_SMS = ""
        SUB_PLAYER = ""

    SUB_FIRST_NAME = st.text_input(
        "First Name:",
        SEL_FIRST_NAME,
        256,
        key="_reg_first_name",
    )
    SUB_LAST_NAME = st.text_input(
        "Last Name:", SEL_LAST_NAME, 256, key="_reg_last_name"
    )
    SUB_EMAIL = st.text_input("Email:", SEL_EMAIL, 256, key="_reg_email")
    SUB_SMS = st.text_input(
        "Mobile Number (+12224446666):", SEL_SMS, 256, key="_reg_sms"
    )
    SUB_OPT_IN = st.checkbox("Opt-In", SEL_OPT_IN, key="_reg_opt_in")

    submitted = st.form_submit_button("Submit")
    if submitted:
        if SEL_OPT_IN == 1:
            SEL_OPT_IN = True
        else:
            SUB_OPT_IN = False

        WRITE_QUERY = "UPDATE players SET first_name = :1, last_name = :2, opt_in = :3, sms = :4 WHERE email = :5"  # noqa: E501

        # Execute the query with parameters
        conn.cursor().execute(
            WRITE_QUERY,
            (
                SUB_FIRST_NAME,
                SUB_LAST_NAME,
                SUB_OPT_IN,
                SUB_SMS,
                SUB_PLAYER,
            ),
        )

        st.write("Query:", WRITE_QUERY)
        st.write("First Name:", SUB_FIRST_NAME)
        st.write("Last Name:", SUB_LAST_NAME)
        st.write("E-Mail:", SUB_EMAIL)
        st.write("Opt In:", SUB_OPT_IN)
        st.write("SMS:", SUB_SMS)
        st.write("Player:", SUB_PLAYER)
