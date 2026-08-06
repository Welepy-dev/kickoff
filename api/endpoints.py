import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import COMPETITION_IDS
from .client import get

# Small shared pool: keeps the fan-out under the API rate limit. Combined
# with the 429 backoff in client.get, the first (uncached) run succeeds
# instead of bursting ~10 parallel requests.
_EXECUTOR = ThreadPoolExecutor(max_workers=2)
atexit.register(_EXECUTOR.shutdown, wait=False)


def get_competitions() -> dict:
    return get("/competitions")


def get_matches(competition_id: int) -> dict:
    return get(f"/competitions/{competition_id}/matches")


def get_top_scorers(competition_id: int) -> dict:
    return get(f"/competitions/{competition_id}/scorers")


def get_standings(competition_id: int) -> dict:
    return get(f"/competitions/{competition_id}/standings")


def _fetch_all(fn, competition_ids: list[int]) -> list[dict | None]:
    """Fetch one endpoint for every competition.

    A failing competition (404, rate limit, …) yields ``None`` instead of
    aborting the whole batch, so the rest of the data is still shown.
    """
    results: list[dict | None] = [None] * len(competition_ids)
    future_to_index = {
        _EXECUTOR.submit(fn, competition_id): i
        for i, competition_id in enumerate(competition_ids)
    }
    for future in as_completed(future_to_index):
        i = future_to_index[future]
        try:
            results[i] = future.result()
        except Exception:
            results[i] = None
    return results


def get_all_standings() -> list[dict | None]:
    return _fetch_all(get_standings, COMPETITION_IDS)


def get_all_matches() -> list[dict | None]:
    return _fetch_all(get_matches, COMPETITION_IDS)


def get_all_top_scorers() -> list[dict | None]:
    return _fetch_all(get_top_scorers, COMPETITION_IDS)
