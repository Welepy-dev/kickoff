from dataclasses import dataclass 

@dataclass
class Scorer:
    id: int
    player: str
    gamesPlayed: int
    goals: int 
    penalties: int
    assists: int
    competition: str
    competition_id: int
    nationality: str
    team: str
    teamId: int

def parse_scorers(data: list | dict) -> list[Scorer]:
    if isinstance(data, dict):
        data = [data]

    scorers = []

    for item in data:
        for player in item["scorers"]:
            scorers.append(
                Scorer(
                    id=player["player"]["id"],
                    player=player["player"]["name"],
                    gamesPlayed=player["playedMatches"],
                    goals=player["goals"],
                    penalties=player["penalties"],
                    assists=player["assists"],
                    competition=item["competition"]["name"],
                    competition_id=item["competition"]["id"],
                    nationality=player["player"]["nationality"],
                    team=player["team"]["shortName"],
                    teamId=player["team"]["id"]
                )
            )
    return scorers
