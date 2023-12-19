"""
List of all scoring rules
"""
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from utilities import check_password, get_user_name

st.set_page_config(page_title="Draft Order", page_icon=":skull_and_crossbones:")

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
df_order["SCALED_RANDOM"] = scaler.fit_transform(df_order[["RANDOM_NUMBER"]]).round(3)
df_order["TOTAL"] = df_order["SCALED_ORDER"] + df_order["SCALED_RANDOM"] + df_order["SCALED_SCORE"] * -1
df_sorted = df_order.sort_values(by="TOTAL", ascending=False)

st.subheader("2024 Draft Order")

st.markdown(
    """

**Draft Order**:
- Draft order has been computed to wegh the prior year's draft order along with the number of points scored by the player.  The high draft order, and higher scores peanalized your spot in the new order.
- Additionally, for those that came later in the process, a random number has been applied that helps shuffle users who didn't play last year a little bit.
- Formula for MinMax Scaling: 
    - `X_std = (X - X.min) / (X.max - X.min) X_scaled = X_std * (max - min) + min`.
- Finally the calculation is: `ORDER + RANDOM + (SCORE * -1)`.

"""
)

st.dataframe(df_sorted, use_container_width=True)