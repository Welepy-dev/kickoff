import os
import time
from pathlib import Path

import requests_cache
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")

if not API_TOKEN:
    raise RuntimeError(
        "API_TOKEN is not set. Copy .env.example to .env and fill it in."
    )
if not BASE_URL:
    raise RuntimeError(
        "BASE_URL is not set. Copy .env.example to .env and fill it in."
    )

_CACHE_DIR = Path.home() / ".cache" / "kickoff"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CACHE_PATH = str(_CACHE_DIR / "football_cache")

# Reuse a single session (connection pooling + SQLite caching).
_session = requests_cache.CachedSession(
    _CACHE_PATH,
    backend="sqlite",
    expire_after=3600,
    allowable_methods=["GET"],
    match_headers=False,
    serializer="json",
    connection_kwargs={"check_same_thread": False},
)
_session.headers.update({"X-Auth-Token": API_TOKEN})

_TIMEOUT = 10
_MAX_RETRIES = 3


def get(path: str, params=None):
    """GET a JSON payload with a short retry/backoff on rate limiting (429)."""
    for attempt in range(_MAX_RETRIES):
        response = _session.get(
            f"{BASE_URL}{path}",
            params=params,
            timeout=_TIMEOUT,
        )
        if response.status_code == 429 and attempt < _MAX_RETRIES - 1:
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2 ** attempt
            time.sleep(delay)
            continue
        response.raise_for_status()
        return response.json()
