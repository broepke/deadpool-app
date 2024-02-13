# app/Dockerfile

# Use the ARM-compatible base image for Python 3.11
FROM arm64v8/python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/broepke/deadpool-app.git .

RUN pip3 install -r requirements.txt

# Copy the secrets.toml file from the local machine to the image
COPY secrets.toml /app/.streamlit/secrets.toml

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]