import streamlit as st
from dp_utilities import check_password

st.set_page_config(page_title="Death Wall", page_icon=":skull:")

st.title("Death Wall :skull_and_crossbones:")

email, user_name, authenticated = check_password()
if authenticated:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Joyce Randolph")
        st.write(
            "Joyce Randolph (October 21, 1924 - January 13, 2024) was an American actress of stage and television, best known for playing Trixie Norton on The Jackie Gleason Show and the television sitcom The Honeymooners."
        )  # noqa: E501
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/0/0e/Joyce_Randolph_1963_%28cropped%29.JPG"
        )  # noqa: E501

    with col2:
        st.subheader("Jonnie Irwin")
        st.write(
            "Jonathan James Irwin (18 November 1973 - 2 February 2024) was an English television presenter, writer, lecturer, businessman and property expert. He was best known for presenting the Channel 4 lifestyle programme A Place in the Sun between 2004 and 2021, as well as the BBC daytime programme Escape to the Country between 2010 and 2023."
        )  # noqa: E501
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/f/fd/JonnieIrwin.JPG"
        )  # noqa: E501

    with col1:
        st.subheader("Carl Weathers")
        st.write(
            "Carl Weathers (January 14, 1948 - February 1, 2024) was an American actor, director and gridiron football linebacker. His roles included boxer Apollo Creed in the first four Rocky films (1976-1985), Colonel Al Dillon in Predator (1987), Chubbs Peterson in Happy Gilmore (1996), and Combat Carl in the Toy Story franchise. He also portrayed Det. Beaudreaux in the television series Street Justice (1991-1993) and a fictionalized version of himself in the comedy series Arrested Development (2004, 2013), and voiced Omnitraxus Prime in Star vs. the Forces of Evil (2017-2019). He had a recurring role as Greef Karga in the Star Wars series The Mandalorian (2019-2023), for which he was nominated for the Primetime Emmy Award for Outstanding Guest Actor in a Drama Series."
        )  # noqa: E501
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Carl_Weathers_%28cropped_3_by_4%29.jpg/440px-Carl_Weathers_%28cropped_3_by_4%29.jpg"
        )  # noqa: E501

    with col2:
        st.subheader("Toby Keith")
        st.write(
            """Toby Keith Covel (July 8, 1961 - February 5, 2024), known professionally as Toby Keith, was an American country music singer, songwriter, record producer, and actor. In the 1990s, he released his first four studio albums—Toby Keith (1993), Boomtown (1994), Blue Moon (1996) and Dream Walkin' (1997)—and Greatest Hits Volume One (Toby Keith album) under Mercury Records. These albums all earned gold or higher certification and had several top ten singles, including his chart-topping debut "Should've Been a Cowboy"."""
        )  # noqa: E501
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Playing_to_the_base%2C_Toby_Keith_sings_at_Camp_Buehring_during_his_%27Live_In_Overdrive%27_USO_tour_120426-A-OQ455-001.jpg/440px-Playing_to_the_base%2C_Toby_Keith_sings_at_Camp_Buehring_during_his_%27Live_In_Overdrive%27_USO_tour_120426-A-OQ455-001.jpg"
        )  # noqa: E501
