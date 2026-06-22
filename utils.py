PREMIERLEAGUE_ID = 2021
UCL_ID = 2001
PRIMEIRALIGA_ID = 2017
EREDIVISIE_ID = 2003
BUNDESLIGA_ID = 2002
LIGUE1_ID = 2015
SERIEA_ID = 2019
WORLDCUP_ID = 2000
EURO_ID = 2018
LALIGA_ID = 2014

COMPETITION_IDS = [
    PREMIERLEAGUE_ID, PRIMEIRALIGA_ID, LIGUE1_ID, SERIEA_ID,
    EREDIVISIE_ID, UCL_ID, BUNDESLIGA_ID, WORLDCUP_ID, EURO_ID, LALIGA_ID
]

def get_competition_id(competition: str) -> int:
    if competition == "Champions League":
        return UCL_ID
    if competition == "Europa League":
        return EURO_ID
    if competition == "Premier League":
        return PREMIERLEAGUE_ID
    if competition == "Primeira Liga":
        return PRIMEIRALIGA_ID
    if competition == "World Cup":
        return WORLDCUP_ID
    if competition == "Eredivisie":
        return EREDIVISIE_ID
    if competition == "Bundesliga":
        return BUNDESLIGA_ID
    if competition == "Serie A":
        return SERIEA_ID
    if competition == "Ligue 1":
        return LIGUE1_ID
    if competition == "Laliga":
        return LALIGA_ID
    return 1

