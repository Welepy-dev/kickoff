import os
import requests
import requests_cache
from dotenv import load_dotenv

requests_cache.install_cache(
    "football_cache",
    expire_afte=432000
)

load_dotenv()
API_KEY = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")

def get(path: str, params=None):
    headers = {
        "X-Auth-Token": API_KEY
    }

    response = requests.get(
        f"{BASE_URL}{path}",
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    # print(response.status_code)
    # print(response.text)

    return (response.json())
