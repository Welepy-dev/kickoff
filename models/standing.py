from dataclasses import dataclass

@dataclass
class Standing:
    team: str
    team_id: int
    competition: str
    competition_id: int
    playedGames: int
    wins: int
    draws: int
    losses: int
    goalDifference: int
    goalsFor: int
    points: int
    position: int

def parse_standings(data: list) -> list[Standing]:
    print(data)
    return []
