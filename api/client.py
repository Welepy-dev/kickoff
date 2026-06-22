import os
import requests_cache
from dotenv import load_dotenv

# Use a thread-safe SQLite cache backend
requests_cache.install_cache(
    "football_cache",
    backend="sqlite",
    expire_after=3600,
    allowable_methods=["GET"],
    match_headers=False,
    serializer="json",
    use_temp=False,
    connection_kwargs={"check_same_thread": False},
)

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

def get(path: str, params=None):
    response = _session.get(
        f"{BASE_URL}{path}",
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()
