#!/bin/bash

# Setup the PATH variable
export PATH=~/.local/bin:$PATH
cd /home

# Create the "streamlit" user and set up their environment
new_username="streamlit"
password=$(aws secretsmanager get-secret-value --secret-id streamlit-ec2-user-pw \
--query 'SecretString' | jq -r '. | fromjson | .key')
sudo useradd -m -s /bin/bash $new_username
echo "$new_username:$password" | chpasswd

# Set up the "streamlit" user's environment and create an alias
sudo -u streamlit -i bash -c 'echo "alias python=python3" >> ~/.bashrc'

# Reload the "streamlit" user's environment
sudo -u streamlit -i bash -c "source ~/.bashrc"

# Install PIP and Python under the "streamlit" user
sudo -u streamlit -i bash -c "curl -O https://bootstrap.pypa.io/get-pip.py"
sudo -u streamlit -i bash -c "python3 /home/streamlit/get-pip.py --user"
sudo -u streamlit -i bash -c "sudo yum install -y python3-devel"
sudo -u streamlit -i bash -c "sudo yum install -y gcc"
sudo -u streamlit -i bash -c "sudo yum install -y git"

# Install GIT for all users
sudo yum install -y git

# Install Python Required Packages under the "streamlit" user
sudo -u streamlit -i bash -c "pip install --user --upgrade \
    flask \
    fuzzywuzzy \
    openai \
    tabulate \
    numexpr \
    python-Levenshtein \
    twilio \
    streamlit \
    streamlit-authenticator \
    langchain \
    langchain-openai \
    langchain-community \
    langchain-experimental==0.0.49 \
    langchainhub \
    'Jinja2>=3.1.2' \
    snowflake-snowpark-python"

# Git Clone the source
sudo -u streamlit -i bash -c 'git clone https://github.com/broepke/deadpool-app'

# Create and configure the Prefect Agent service
cd /etc/systemd/system
cat <<EOF | sudo tee /etc/systemd/system/streamlit-agent.service
[Unit]
Description=Streamlit Agent

[Service]
User=streamlit
WorkingDirectory=/home/streamlit/deadpool-app
ExecStart=/home/streamlit/.local/bin/streamlit run /home/streamlit/deadpool-app/Home.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable streamlit-agent
sudo systemctl start streamlit-agent

# Reload environment variables to reflect changes
source ~/.bashrc

# Fetch secrets from AWS Secrets Manager
snowflake_account=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."snow-account"')
snowflake_password=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."snow-password"')
twilio_sid=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."twilio-sid"')
twilio_token=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."twilio-token"')
apify_main_bearer=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."apify-main-bearer"')
apify_base_bearer=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."apify-base-bearer"')
openai_key=$(aws secretsmanager get-secret-value --secret-id streamlit-secrets --query 'SecretString' | jq -r '. | fromjson | ."openai-key"')

# Create the ".streamlit" directory under "/home/streamlit/deadpool-app"
sudo -u streamlit mkdir -p /home/streamlit/deadpool-app/.streamlit

# Create the "secrets.toml" file and write the configuration to it with fetched secrets
sudo -u streamlit bash -c 'cat > /home/streamlit/deadpool-app/.streamlit/secrets.toml <<EOF
[connections.snowflake]
account = "'"$snowflake_account"'"
user = "STREAMLIT"
password = "'"$snowflake_password"'"
role = "ENGINEER"
warehouse = "DEADPOOL"
database = "DEADPOOL"
schema = "PROD"
client_session_keep_alive = true

[twilio]
account_sid = "'"$twilio_sid"'"
auth_token = "'"$twilio_token"'"

[apify]
main_api = "https://bs-flowise.onrender.com/api/v1/prediction/d42ec856-bcc6-43cd-a9d3-e17abd8a5522"
main_bearer = "'"$apify_main_bearer"'"
base_api = "https://bs-flowise.onrender.com/api/v1/prediction/92edbb37-bef3-4475-8dbf-f2122d510818"
base_bearer = "'"$apify_base_bearer"'"

[llm]
openai_api_key = "'"$openai_key"'"
EOF'

# GitHub Personal Access Token
github_token=$(aws secretsmanager get-secret-value --secret-id github-pat \
--query 'SecretString' | jq -r '. | fromjson | .key')

sudo -u streamlit bash -c 'cat <<EOF > /home/streamlit/github_webhook.py
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/github-webhook", methods=["POST"])
def github_webhook():
    payload = request.json
    if payload["ref"] == "refs/heads/MAIN":
        subprocess.run(["git", "-C", "/home/streamlit/deadpool-app", "pull"])
    return jsonify({"message": "Webhook received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF'


# Create a systemd service unit file for the Flask server
cat <<EOF | sudo tee /etc/systemd/system/github-webhook.service
[Unit]
Description=GitHub Webhook Service
After=network.target

[Service]
User=streamlit
WorkingDirectory=/home/streamlit
ExecStart=/usr/bin/python3 /home/streamlit/github_webhook.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the GitHub Webhook service
sudo systemctl daemon-reload
sudo systemctl enable github-webhook
sudo systemctl start github-webhook

# Install DataDog
export DD_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id DataDog \
    --query 'SecretString' --output text) 
export DD_SITE="datadoghq.com"
export DD_APM_INSTRUMENTATION_ENABLED=host
sudo DD_API_KEY="$DD_API_KEY" DD_SITE="$DD_SITE" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"