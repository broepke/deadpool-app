import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['human-ecology']).generate()

print()
print(hashed_passwords[0])
