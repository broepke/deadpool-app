import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


st.set_page_config(page_title="Forgot Password", page_icon=":skull:")
st.title("Forgot Password :skull_and_crossbones:")

# Get all credentials
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    auto_hash=True,
)


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
        subject = "Your New Password"
        body = f"Hello,\n\nYour new password is:\n\n{new_random_password}\n\nPeace out,\nThe Arbiter"
        if send_email(email_of_forgotten_password, subject, body):
            st.success("Email sent successfully!")

            # Update the Yaml file as well
            # with open("config.yaml", "w") as file:
            #     yaml.dump(config, file, default_flow_style=False)
        else:
            st.error("Failed to send the email.")
    elif username_of_forgotten_password is False:
        st.error("Username not found")
except Exception as e:
    st.error(e)
