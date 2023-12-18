"""
Streamlit main app
"""
import random
import streamlit as st
from utilities import check_password, get_user_name, the_arbiter


if not check_password():
    st.stop()

# Get information about the user
email = st.session_state["username"]
user_name = get_user_name(email)

# add the username at the top so we know we're the right person.
st.write(email)

# Add some text
st.title("Deadpool 2024 :skull_and_crossbones:")

# Generate a little more randomness into the prompt
tone = ["sarcastic", "dry humor", "playful"]
insult = ["pick strategy", "their current"]
humor = ["puns", "wordplay", "dad joke"]

selected_tone = random.choice(tone)
selected_insult = random.choice(insult)
selected_humor = random.choice(humor)


prompt = (
    """Come up with 2-3 """
    + selected_tone
    + """ sentences about the user """
    + user_name
    + """ and make it sassy. You can lightly insult them personally based on their """
    + selected_insult
    + """.  This is all in good fun done in the style of hummor of """
    + selected_humor
)

# output = the_arbiter(
#     {
#         "question": prompt,
#     }
# )

# st.markdown("**A message from The Arbiter:** " + output["text"])

# st.divider()

st.markdown(
    """
Welcome to **Deadpool 2024**, the annual fantasy draft where every pick you make has you cheering for a famous person's death! Deadpool is not just a game; it's a journey into the degenerate behavior that you've been known for. Feel the excitement build as you assemble your dream (death) team, strategizing against rivals in a quest for glory. Here, every round is a spectacle; every decision echoes with the crowd's roar. **Deadpool 2024** is more than fantasy; it's where celebrity death enthusiasts become architects of their destiny. Get ready to experience the exhilaration of victory and the rush of competition like never before. Buckle up, and let the games begin!
           """
)

st.image("deadpool.png", "The Arbiter")
