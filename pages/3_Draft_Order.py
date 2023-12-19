"""
List of all scoring rules
"""
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from utilities import check_password, get_user_name

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except:
    st.write("Please login again")

conn = st.connection("snowflake")


def load_picks_table(table):
    session_picks = conn.session()
    return session_picks.table(table).to_pandas()


df_order = load_picks_table("draft_selection")

# Scale the data and add columns
scaler = MinMaxScaler()
df_order["SCALED_ORDER"] = scaler.fit_transform(df_order[["PRIOR_DRAFT"]]).round(3)
df_order["SCALED_SCORE"] = scaler.fit_transform(df_order[["SCORE"]]).round(3)
df_order["TOTAL"] = df_order["SCALED_ORDER"] + df_order["SCALED_SCORE"] * -1
df_sorted = df_order.sort_values(by="TOTAL", ascending=False)

st.subheader("2024 Draft Order")

st.dataframe(df_sorted, use_container_width=True)