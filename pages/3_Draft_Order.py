"""
List of all scoring rules
"""
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from utilities import check_password, get_user_name, load_snowflake_table

st.set_page_config(page_title="Draft Order", page_icon=":skull_and_crossbones:")

if not check_password():
    st.stop()

try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except KeyError:
    st.write("Please login again")

conn = st.connection("snowflake")


df_ord = load_snowflake_table(conn, "draft_selection")

# Scale the data and add columns
sc = MinMaxScaler()
df_ord["SCALED_ORDER"] = sc.fit_transform(df_ord[["PRIOR_DRAFT"]]).round(3)
df_ord["SCALED_SCORE"] = sc.fit_transform(df_ord[["SCORE"]]).round(3)
df_ord["SCALED_RANDOM"] = sc.fit_transform(df_ord[["RANDOM_NUMBER"]]).round(3)
df_ord["TOTAL"] = (
    df_ord["SCALED_ORDER"] + df_ord["SCALED_RANDOM"] + df_ord["SCALED_SCORE"] * -1
)
df_sorted = df_ord.sort_values(by="TOTAL", ascending=False).reset_index(drop=True)

st.subheader("2024 Draft Order")

st.markdown(
    """

**Draft Order**:
- Draft order has been computed to weigh the prior year's draft order and the number of points scored by the player.  The high draft order and higher scores penalized your spot in the new order.
- Additionally, a random number has been applied for those who came later, which helps shuffle users who didn't play a little last year.
- All numbers are normalized between 0 and 1.
- Finally the calculation is: `ORDER + RANDOM + (SCORE * -1)`.
"""  # noqa: E501
)

st.dataframe(df_sorted, use_container_width=True)

st.caption(
    "Note: There is a small adjustment.  Due to the fact that Luke is a whiny bitch, the Aribter has allowed the swapping of positions for Brian Roepke and Luke Marble.  The Arbiter - who's all judgements are final and binding. Peace out"
)
