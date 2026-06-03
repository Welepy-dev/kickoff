from api.constants import BUNDESLIGA_ID, EREDIVISIE_ID, EURO_ID, LIGUE1_ID, PREMIERLEAGUE_ID, PRIMEIRALIGA_ID, SERIEA_ID, UCL_ID, WORLDCUP_ID
from .client import get

def get_competitions() -> dict:
    return (get("/competitions"))

def get_matches(id: int) -> dict:
    return (get(f"/competitions/{id}/matches"))

def get_all_matches():
    matches = []
    matches.extend([
        get_matches(PREMIERLEAGUE_ID),
        get_matches(PRIMEIRALIGA_ID),
        get_matches(LIGUE1_ID),
        get_matches(SERIEA_ID),
        get_matches(EREDIVISIE_ID),
        get_matches(UCL_ID),
        get_matches(BUNDESLIGA_ID),
        get_matches(WORLDCUP_ID),
        get_matches(EURO_ID)
    ])
    return (matches)

def get_previous_matches(id: int) -> dict:
    matches = get_matches(id)
    #search in the list for the date and slice it from todays date to before
    return (matches)

def get_top_scorers(id: int) -> dict:
    return (get(f"/competitions/{id}/scorers"))

def get_all_top_scorers():
    scorers = []
    scorers.extend([
        get_top_scorers(PREMIERLEAGUE_ID),
        get_top_scorers(PRIMEIRALIGA_ID),
        get_top_scorers(LIGUE1_ID),
        get_top_scorers(SERIEA_ID),
        get_top_scorers(EREDIVISIE_ID),
        get_top_scorers(UCL_ID),
        get_top_scorers(BUNDESLIGA_ID),
        get_top_scorers(WORLDCUP_ID),
        get_top_scorers(EURO_ID)
    ])
    return (scorers)
