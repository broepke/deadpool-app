"""
Streamlit main app
"""
import random
import time
import streamlit as st
from dp_utilities import check_password

st.set_page_config(page_title="Deadpool", page_icon=":skull:")

email, user_name, authenticated = check_password()
if authenticated:
    # --- Main Application Code
    st.title("Deadpool 2024 :skull_and_crossbones:")

    # Generate a little more randomness into the prompt
    tone = ["sarcastic", "dry humor", "playful"]
    insult = ["pick strategy", "their current"]
    humor = ["puns", "wordplay", "dad joke", "haiku", "rap battle"]
    style = [
        "an Eminem rap song?",
        "Shakeare had written it?",
        "an Jerry Seinfeld stand up bit?",
        "Hemmingway had written it?",
        "an F. Scott Fitzgerlald novel?",
        "Huter S. Thompson had written it?",
        "Captain Jack Sparrow from Pirates of the Carribean?",
    ]

    selected_tone = random.choice(tone)
    selected_insult = random.choice(insult)
    selected_humor = random.choice(humor)
    selected_style = random.choice(style)

    prompt = (
        "I want you to create a creative insult for the user "
        + user_name
        + " but can you make it like the style of "
        + selected_humor
    )

    try:
        start_time = time.time()
        # output = the_arbiter(prompt, arbiter_version="base")
        output = "Greetings, savages. All judgements are final."

        # Calculate the time taken and print it
        end_time = time.time()
        time_taken = end_time - start_time
        st.markdown("**A message from The Arbiter:** " + output)

    except Exception as e:
        st.write(e)
        st.write("Welcome Back, " + user_name)

    st.image("arbiter.jpg", "The Arbiter")

    st.caption(prompt)
    st.caption(f"Time taken to load: {time_taken:.2f} seconds")
