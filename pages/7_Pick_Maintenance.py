import streamlit as st
from Deadpool import check_password


def save_value(key):
    st.session_state[key] = st.session_state["_" + key]


def get_value(key):
    st.session_state["_" + key] = st.session_state[key]


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
except:
    st.write("Please login again")

if email != "broepke@gmail.com":
    st.write("Not authorized")
else:
    st.title("Pick Maintenance Tools")

    # Initialize important varibles
    sel_first_name = ""
    sel_last_name = ""
    sel_email = ""
    sel_sms = ""
    sel_opt_in = True

    # Initialize connection.
    conn = st.connection("snowflake")

    # Get a list off all curent players
    @st.cache_data
    def load_picks_table():
        session_picks = conn.session()
        return session_picks.table("picks").to_pandas()

    df_picks = load_picks_table()
    
    df_picks_2024 = df_picks[df_picks['YEAR'] == 2024]
    
    df_players_list = df_picks_2024["NAME"].to_list()

    st.header("Pick Selection")

    # Load all the players into a drop down for easy selection
    with st.form("Pick to Update"):
        sel_player = st.selectbox(
            "Select a Player", df_players_list, key="sel_selected_player"
        )
        submitted = st.form_submit_button("Choose Player")

        if submitted:
            filtered_df = df_picks_2024[df_picks_2024["NAME"] == sel_player]

            if not filtered_df.empty:
                sel_first_name = filtered_df.iloc[0]["FIRST_NAME"]
                sel_last_name = filtered_df.iloc[0]["LAST_NAME"]
                sel_email = filtered_df.iloc[0]["EMAIL"]
                sel_sms = filtered_df.iloc[0]["SMS"]
                sel_opt_in = filtered_df.iloc[0]["OPT_IN"]

                st.session_state["reg_first_name"] = sel_first_name
                st.session_state["reg_last_name"] = sel_last_name
                st.session_state["reg_email"] = sel_email
                st.session_state["reg_sms"] = sel_sms
                st.session_state["reg_opt_in"] = sel_opt_in
                st.session_state["reg_player"] = sel_email

            else:
                print("No user found with the given email")

    st.header("Update Player Information")

    with st.form("Registration"):
        
        try:
            sel_first_name = st.session_state["reg_first_name"]
            sel_first_name = st.session_state["reg_first_name"]
            sel_last_name = st.session_state["reg_last_name"]
            sel_email = st.session_state["reg_email"]
            sel_opt_in = st.session_state["reg_opt_in"]
            sel_sms = st.session_state["reg_sms"]
            sub_player = st.session_state["reg_player"]
        except:
            sel_first_name = ""
            sel_last_name = ""
            sel_email = ""
            sel_opt_in = ""
            sel_sms = ""
            sub_player = ""

        
        sub_first_name = st.text_input(
            "First Name:",
            sel_first_name,
            256,
            key="_reg_first_name",
        )
        sub_last_name = st.text_input(
            "Last Name:", sel_last_name, 256, key="_reg_last_name"
        )
        sub_email = st.text_input("Email:", sel_email, 256, key="_reg_email")
        sub_sms = st.text_input("Mobile Number:", sel_sms, 256, key="_reg_sms")
        sub_opt_in = st.checkbox("Opt-In", sel_opt_in, key="_reg_opt_in")

        submitted = st.form_submit_button("Submit")
        if submitted:
            
            if sel_opt_in == 1:
                sel_opt_in = True
            else:
                sub_opt_in = False
        

            write_query = "UPDATE players SET first_name = :1, last_name = :2, email = :3, opt_in = :4, sms = :5 WHERE email = :6"

            # # Execute the query with parameters
            conn.cursor().execute(
                write_query,
                (
                    sub_first_name,
                    sub_last_name,
                    sub_email,
                    sub_opt_in,
                    sub_sms,
                    sub_player,
                ),
            )

            st.write(write_query)
            st.write(sub_first_name)
            st.write(sub_last_name)
            st.write(sub_email)
            st.write(sub_opt_in)
            st.write(sub_sms)
            st.write(sub_player)
