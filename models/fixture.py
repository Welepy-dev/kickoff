from dataclasses import dataclass

@dataclass
class Fixture:
    name: str
    competition: str
    awayTeam: str
    homeTeam: str
    matchday: int
    score: str
    winner: str
    date: str
