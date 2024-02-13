# Use the ARM-compatible base image for Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Clone your app repository
RUN git clone https://github.com/broepke/deadpool-app.git .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the webhook script into the container
COPY github_webhook.py /app/github_webhook.py

# Copy the dynamically generated secrets.toml as secrets.toml into the image
COPY secrets.toml /app/.streamlit/secrets.toml

# Setup Supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports for Streamlit and Flask
EXPOSE 8501 5000 

# Use Supervisord to run both services
CMD ["/usr/bin/supervisord"]
