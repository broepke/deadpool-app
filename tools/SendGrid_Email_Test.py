import streamlit as st
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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

# Streamlit UI for triggering the email
def main():
    st.title("Password Reset Email Sender")

    receiver_email = st.text_input("Enter the user's email address:")
    reset_code = st.text_input("Enter the reset password:")
    subject = "Your Password Reset Code"

    if st.button("Send Email"):
        if receiver_email and reset_code:
            body = f"Hello,\n\nYour password reset code is: {reset_code}\n\nBest regards,\nYour App Team"
            if send_email(receiver_email, subject, body):
                st.success("Email sent successfully!")
            else:
                st.error("Failed to send the email.")
        else:
            st.warning("Please enter the email address and reset code.")

if __name__ == "__main__":
    main()