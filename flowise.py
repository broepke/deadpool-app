import requests


API_URL = "https://flowise-1-irl9.onrender.com/api/v1/prediction/294d5cef-e400-4de7-b74c-920994cd2c58"


def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()


output = query(
    {
        "question": "Hey, how are you?",
    }
)
