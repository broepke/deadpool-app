import streamlit as st
from utilities import check_password, get_user_name

if not check_password():
    st.stop()  # Do not continue if check_password is not True.
    
try:
    st.write(st.session_state["username"])
    email = st.session_state["username"]
    user_name = get_user_name(email)
except:
    st.write("Please login again")

st.header("App Considerations")
st.markdown(
    """
1. The application may experience bugs from time to time - please report them in the DM.
2. When you click a navigation link in the side-bar, sometimes the page doesn't load with the new content.  Just click the page again and it will load properly.
3. If you refresh the page utilizing your browser, it will ask you to log in again.  A better way to refresh is just simple click the link in the navigation bar again.
4. This application works best on a desktop browser.  The Mobile does work, but is flakey.
5. For the best results, use the same spelling of the person from their Wikipedia page.  For example, Chris Burke was chosen in the past, his Wiki page's title is "Chris Burke (actor)" - if you enter this, it will speed up the disambiguation of the pick.  Not critical but the arbiter will appreciate it.
6. If you want a password or email change, please contact the arbiter.
"""
)
