"""
List of all scoring rules
"""
import streamlit as st
from utilities import check_password

st.set_page_config(page_title="Rules", page_icon=":skull:")

st.title("Rules :skull_and_crossbones:")

email, user_name, authticated = check_password()
if authticated:
    st.title("Rules for Online Dead Pool 2024")

    st.markdown(
        """
    1. **Entry and Participation**:
        - All participants will draft their picks in January through this site.
        - The process will happen as a "Round Robin" based on the _Draft Order_
        - Participants select a list of 20 public figures they predict will pass away in 2024.
    2. **Selection Criteria**:
        - Only public figures (celebrities, politicians, athletes, etc.) may be selected.
        - At least 50% of the players must know each selection, or be easily validated from Wikipedia.
        - You cannot pick Willie Nelson.  He is the new Betty White.
    3. **Points System**:
        - The total points of the death will be calculated as **50 + (100-AGE)**.
        - E.g., the death of a person who's 90 years old will be 60 points.
        - First Blood will be awarded an additional **25 points**.
        - Last Blood will be awarded an additional **25 points**.
        - At the end of each calendar quarter, the person with the most points in that calendar quarter will be awarded **5 points**.
        - If you pick a dead person, which will be checked automatically after the draft finishes, you will lose that pick and receive 0 points.
    4. **Trade Days**:
        - Once per quarter, each participant may draft / trade **one** new celebrity in exchange for another.
    5. **Duration**:
        - The dead pool runs from January 1, 2024, to December 31, 2024, at Midnight.
        - The draft will happen in January at a time condusive to participants.
        - Given the new system, we should close the draft no later than January 31 at Midnight.  The Arbiter will have the final say.
        - If any celebrity dies during the draft process, it's allowed if the draft was already recorded.
    6. **Draft Order**:
        - Draft order has been computed to weigh the prior year's draft order and the number of points scored by the player.  The high draft order and higher scores penalized your spot in the new order.
        - Additionally, a random number has been applied for those who came later, which helps shuffle users who didn't play a little last year.
    7. **Privacy and Confidentiality**:
        - Participant information must be kept confidential.
        - Lists of predictions should not be publicized or shared outside the pool.
    8. **Dispute Resolution**:
        - The Arbiter's decision is final in all cases of disputes.
    """  # noqa: E501
    )

    st.write("I have Spoken!  Signed the Arbiter")
