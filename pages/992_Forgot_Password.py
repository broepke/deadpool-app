import streamlit as st
import yaml
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dp_utilities import check_password


st.set_page_config(page_title="Forgot Password", page_icon=":skull:")
st.title("Forgot Password :skull_and_crossbones:")

email, user_name, authenticator, config, authenticated = check_password()
subject = "Your New Password"

def send_email(receiver_email, subject, body):
    sender_email = st.secrets["sendgrid"]["sendgrid_sender_email"]
    sendgrid_api_key = st.secrets["sendgrid"]["sendgrid_api_key"]

    # Create the email message
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        if response.status_code == 202:
            return True
        else:
            st.error(f"Failed to send email. Status Code: {response.status_code}")
            return False

    except Exception as e:
        st.error(f"Error: {e}")
        return False


# Forgot password
try:
    username_of_forgotten_password, email_of_forgotten_password, new_random_password = (
        authenticator.forgot_password()
    )
    if username_of_forgotten_password:
        st.success("New password to be sent securely")
        body = f"Hello,\n\nYour new password is: {new_random_password}\n\nBest regards,\nYour App Team"
        if send_email(email_of_forgotten_password, subject, body):
            st.success("Email sent successfully!")
        else:
            st.error("Failed to send the email.")
    elif username_of_forgotten_password is False:
        st.error("Username not found")
except Exception as e:
    st.error(e)

# with open("config.yaml", "w") as file:
#     yaml.dump(config, file, default_flow_style=False)
