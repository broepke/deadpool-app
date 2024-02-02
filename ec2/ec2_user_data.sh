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
sudo -u streamlit -i bash -c "pip install --user \
    fuzzywuzzy \
    python-Levenshtein \
    twilio \
    streamlit \
    streamlit-authenticator \
    langchain \
    langchain-openai \
    langchain-community \
    langchain-experimental \
    langchainhub \
    openai \
    tabulate \
    numexpr \
    Jinja2 \
    snowflake-snowpark-python[pandas]"

# Git Clone the source
sudo -u streamlit -i bash -c 'git clone https://github.com/broepke/deadpool-app'

# Create and configure the Prefect Agent service
cd /etc/systemd/system
cat <<EOF | sudo tee /etc/systemd/system/streamlit-agent.service
[Unit]
Description=Streamlit Agent

[Service]
User=streamlit
WorkingDirectory=/home/streamlit
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

# Install DataDog
export DD_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id DataDog \
    --query 'SecretString' --output text) 
export DD_SITE="datadoghq.com"
export DD_APM_INSTRUMENTATION_ENABLED=host
sudo DD_API_KEY="$DD_API_KEY" DD_SITE="$DD_SITE" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"