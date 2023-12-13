"""
List of all scoring rules
"""
import streamlit as st
from Deadpool import check_password

if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st.title("Rules for Online Dead Pool 2024")


st.markdown("""
1. **Purpose and Scope**:
    - This dead pool is intended for entertainment purposes.
    - Participants must be 18 years or older.
2. **Entry and Participation**:
    - Each participant is allowed one entry per year.
    - Participants select a list of 15 public figures they predict will pass away in 2024.
3. **Selection Criteria**:
    - Only public figures (celebrities, politicians, etc.) may be selected.
    - Each selection must be known by 50% of the players.
4. **Points and Betting System**:
    - 100 Points are awarded based on each correct prediction.
    - First death awarded an additional 10 points
    - The scoring system should be defined clearly (e.g., points based on age, profession, etc.).
    - Participants may place bets on their predictions according to the rules set by the organizer.
5. **Duration**:
    - The dead pool runs from January 1, 2024, to December 31, 2024.
    - All predictions must be submitted before the start date.
6. **Ethical Considerations**:
    - Participants are expected to maintain respect and sensitivity towards the individuals listed and their families.
7. **Privacy and Confidentiality**:
    - Participant information must be kept confidential.
    - Lists of predictions should not be publicized or shared outside the pool.
8. **Dispute Resolution**:
    - The arbiter’s decision is final in case of disputes.
    - Rules for handling ties or unusual circumstances should be clearly defined.
9. **Cancellation or Suspension**:
    - The organizer reserves the right to cancel or suspend the pool in case of unforeseen circumstances.
10. **Legal Compliance**:
    - Participants are responsible for ensuring their participation complies with local laws and regulations, including those related to gambling.

### **Additional Notes**

- Regular updates can be provided to participants.
- Organizers should remind participants of the purpose of the pool and the importance of respectful participation.
""")
