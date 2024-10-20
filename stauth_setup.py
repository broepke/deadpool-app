# Note - this can be run on a raw config.yaml file to hash the passwords

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Get all credentials
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"], 
    auto_hash=True
)

with open("config.yaml", "w") as file:
    yaml.dump(config, file, default_flow_style=False)