from api.constants import COMPETITION_IDS 
from .client import get
from concurrent.futures import ThreadPoolExecutor

def get_competitions() -> dict:
    return (get("/competitions"))

def get_matches(id: int) -> dict:
    return (get(f"/competitions/{id}/matches"))

def get_top_scorers(id: int) -> dict:
    return (get(f"/competitions/{id}/scorers"))

def get_standings(id: int) -> dict:
    return(get(f"/competitions/{id}/standings"))

def get_all_standings() -> list:
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_standings, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_all_matches() -> list:
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_matches, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_all_top_scorers() -> list:
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_top_scorers, id) for id in COMPETITION_IDS]
        return [f.result() for f in futures]

def get_match(id: int) -> dict:
    return(get(f"/matches/{id}/"))
