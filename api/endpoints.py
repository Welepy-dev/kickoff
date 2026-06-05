from api.constants import COMPETITION_IDS 
from .client import get
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone, datetime


def get_competitions() -> dict:
    return (get("/competitions"))

def get_matches(id: int) -> dict:
    return (get(f"/competitions/{id}/matches"))

def get_top_scorers(id: int) -> dict:
    return (get(f"/competitions/{id}/scorers"))

def get_standings(id: int) -> dict:
    return(get(f"/competitions/{id}/standings"))

def get_all_matches():
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_matches, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_all_top_scorers():
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_top_scorers, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_all_previous_matches():
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_previous_matches, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_all_next_matches():
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_next_matches, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_previous_matches(id: int):
    matches = get_matches(id)
    cutoff = datetime.now(timezone.utc)
    filtered_matches = []
    for match in matches["matches"]:
        match_date = datetime.fromisoformat(
            match["utcDate"].replace("Z", "+00:00")
        )
        if match_date <= cutoff:
            filtered_matches.append(match)
    return (filtered_matches)

def get_next_matches(id: int):
    matches = get_matches(id)
    cutoff = datetime.now(timezone.utc)
    filtered_matches = []
    for match in matches["matches"]:
        match_date = datetime.fromisoformat(
            match["utcDate"].replace("Z", "+00:00")
        )
        if match_date >= cutoff:
            filtered_matches.append(match)
    return (filtered_matches)

