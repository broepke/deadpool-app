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
4. **Points and Betting System**:
    - 100 Points are awarded based on each correct prediction.
    - The total points of the death will be calculated as `50 + (100-AGE)`.
    - E.g., the death of a person who's 90 years old will be 60 points.
    - First Blood was awarded an additional 25 points.
    - Last Blood awarded an additional 25 points.
    - At the end of each calendar quarter, the person in the lead will be awarded five additional points.
5. **Trade Days**:
    - Once per quarter, each participant may draft / trade **one** new celebrity in exchange for another.
6. **Duration**:
    - The dead pool runs from January 1, 2024, to December 31, 2024.
    - The draft will happen in January.
    - If any celebrity dies during the draft process, it's allowed if the draft was already recorded.
7. **Privacy and Confidentiality**:
    - Participant information must be kept confidential.
    - Lists of predictions should not be publicized or shared outside the pool.
8. **Dispute Resolution**:
    - The judge's decision is final in case of disputes.
""")
