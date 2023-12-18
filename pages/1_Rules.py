"""
List of all scoring rules
"""
import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from Home import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

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


st.title("Rules for Online Dead Pool 2024")


st.markdown(
    """
1. **Purpose and Scope**:
    - This dead pool is intended for entertainment purposes.
2. **Entry and Participation**:
    - All participants will draft their picks in January through this site.
    - The process will happen as a "Round Robin" based on the _Draft Order_
    - Participants select a list of 20 public figures they predict will pass away in 2024.
3. **Selection Criteria**:
    - Only public figures (celebrities, politicians, athletes, etc.) may be selected.
    - At least 50% of the players must know each selection.
4. **Points System**:
    - The total points of the death will be calculated as **50 + (100-AGE)**.
    - E.g., the death of a person who's 90 years old will be 60 points.
    - First Blood was awarded an additional **25 points**.
    - Last Blood awarded an additional **25 points**.
    - At the end of each calendar quarter, the person with the most points in that calendar quarter will be awarded **5 points**. 
5. **Trade Days**:
    - Once per quarter, each participant may draft / trade **one** new celebrity in exchange for another.
6. **Duration**:
    - The dead pool runs from January 1, 2024 at Midnight, to December 31, 2024 at Midnight.
    - The draft will happen in January.
    - If any celebrity dies during the draft process, it's allowed if the draft was already recorded.
7. **Draft Order**:
    - Draft order has been computed to wegh the prior year's draft order along with the number of points scored by the player.  The high draft order, and higher scores peanalized your spot in the new order.
    - Formula: `X_std = (X - X.min) / (X.max - X.min)
X_scaled = X_std * (max - min) + min`.
8. **Privacy and Confidentiality**:
    - Participant information must be kept confidential.
    - Lists of predictions should not be publicized or shared outside the pool.
9. **Dispute Resolution**:
    - The Arbiter's decision is final in all case of disputes.
"""
)

st.subheader("2024 Draft Order")

st.dataframe(df_sorted, use_container_width=True)

st.write("I have Spoken!  Signed the Arbiter")
