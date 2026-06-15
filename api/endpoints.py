from api.constants import COMPETITION_IDS
from .client import get
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_competitions() -> dict:
    return get("/competitions")

def get_matches(id: int) -> dict:
    return get(f"/competitions/{id}/matches")

def get_top_scorers(id: int) -> dict:
    return get(f"/competitions/{id}/scorers")

def get_standings(id: int) -> dict:
    return get(f"/competitions/{id}/standings")

def _fetch_all(fn, ids):
    results = [None] * len(ids)
    with ThreadPoolExecutor(max_workers=len(ids)) as executor:
        future_to_index = {executor.submit(fn, id): i for i, id in enumerate(ids)}
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            results[i] = future.result()
    return results

def get_all_standings() -> list:
    return _fetch_all(get_standings, COMPETITION_IDS)

def get_all_matches() -> list:
    return _fetch_all(get_matches, COMPETITION_IDS)

def get_all_top_scorers() -> list:
    return _fetch_all(get_top_scorers, COMPETITION_IDS)

def get_match(id: int) -> dict:
    return get(f"/matches/{id}/")
