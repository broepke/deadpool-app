"""
List of all scoring rules
"""
import streamlit as st
from Home import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st.title("Rules for Online Dead Pool 2024")


st.markdown("""
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
    - The formula used is `X_std = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
X_scaled = X_std * (max - min) + min`.
8. **Privacy and Confidentiality**:
    - Participant information must be kept confidential.
    - Lists of predictions should not be publicized or shared outside the pool.
9. **Dispute Resolution**:
    - The Arbiter's decision is final in all case of disputes.
""")

st.markdown("""
|FIELD1|FIRST_NAME|LAST_NAME|2023_ORDER|SCORE|scaled_order       |scaled_score      |sum_scaled_columns |
|------|----------|---------|----------|-----|-------------------|------------------|-------------------|
|0     |Andrew    |Frazier  |8         |0    |1.0                |0.0               |1.0                |
|1     |Brian     |Scanen   |6         |0    |0.7142857142857142 |0.0               |0.7142857142857142 |
|2     |John      |Wholihan |4         |0    |0.42857142857142855|0.0               |0.42857142857142855|
|6     |Chris     |Vienneau |7         |67   |0.8571428571428572 |0.5193798449612403|0.33776301218161686|
|3     |Will      |Cokeley  |2         |0    |0.14285714285714285|0.0               |0.14285714285714285|
|7     |Brian     |Roepke   |5         |129  |0.5714285714285714 |1.0               |-0.4285714285714286|
|5     |Alexander |O'Brien  |3         |105  |0.2857142857142857 |0.813953488372093 |-0.5282392026578073|
|4     |Chrissy   |Roepke   |1         |86   |0.0                |0.6666666666666666|-0.6666666666666666|
""")

st.write("I have Spoken!  Signed the Arbiter")