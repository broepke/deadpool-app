import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Get all credentials
with open("../config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

hashed_passwords = stauth.Hasher(['human-ecology']).generate()

print()
print(hashed_passwords[0])
