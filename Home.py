"""
Streamlit main app
"""
import random
import streamlit as st
from utilities import check_password, get_user_name, the_arbiter

st.set_page_config(page_title="Deadpool", page_icon=":skull_and_crossbones:")

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
style = ["Eminem", "shakespeare", "Seinfeld", "cardi b", "fat albert"]

selected_tone = random.choice(tone)
selected_insult = random.choice(insult)
selected_humor = random.choice(humor)
selected_style = random.choice(style)


prompt = (
    "In the lyrical style of "
    + selected_style
    + " come up with 2-3 "
    + selected_tone
    + " sentences about the user "
    + user_name
    + " and make it sassy. You can lightly insult them based on their "
    + selected_insult
    + ".  This is all in good fun done in the style of hummor of "
    + selected_humor
)

st.write(prompt)

try:
    output = the_arbiter(
        {
            "question": prompt,
        }
    )

    st.markdown("**A message from The Arbiter:** " + output["text"])

except Exception as e:
    st.write(e)
    st.write("Welcome Back, " + user_name)

st.image("deadpool.png", "The Arbiter")
