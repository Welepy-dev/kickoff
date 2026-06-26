import os
import time
import requests_cache
from dotenv import load_dotenv
from requests import HTTPError

load_dotenv()
API_KEY = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")

# Reuse a single session (connection pooling)
_session = requests_cache.CachedSession(
    "football_cache",
    backend="sqlite",
    expire_after=3600,
    allowable_methods=["GET"],
    match_headers=False,
    serializer="json",
    connection_kwargs={"check_same_thread": False},
)
_session.headers.update({"X-Auth-Token": API_KEY})

MAX_RETRIES = 5

def get(path: str, params=None):
    for attempt in range(MAX_RETRIES):
        response = _session.get(
            f"{BASE_URL}{path}",
            params=params,
            timeout=10
        )
        if response.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()
    raise HTTPError(f"429 Client Error: rate limit exceeded for {path}")
