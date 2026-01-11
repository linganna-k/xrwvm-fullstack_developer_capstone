import os

import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("backend_url", "http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url",
    "http://localhost:5050/",
)


def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params += f"{key}={value}&"

    request_url = f"{backend_url}{endpoint}?{params}"
    print(f"GET from {request_url}")

    try:
        response = requests.get(request_url, timeout=10)
        return response.json()
    except requests.RequestException as exc:
        print(f"Network exception occurred: {exc}")
        return None


def analyze_review_sentiments(text):
    request_url = f"{sentiment_analyzer_url}analyze/{text}"

    try:
        response = requests.get(request_url, timeout=10)
        return response.json()
    except requests.RequestException as exc:
        print(f"Network exception occurred: {exc}")
        return None


def post_review(data_dict):
    request_url = f"{backend_url}/insert_review"

    try:
        response = requests.post(
            request_url,
            json=data_dict,
            timeout=10,
        )
        return response.json()
    except requests.RequestException as exc:
        print(f"Network exception occurred: {exc}")
        return None
