from dataclasses import dataclass

@dataclass
class Fixture:
    id: int
    name: str
    competition: str
    competition_id: str
    awayTeam: str
    awayTeamCrest: str
    homeTeam: str
    homeTeamCrest: str
    matchday: int
    score: str
    winner: str
    date: str

def parse_fixtures(data: list | dict) -> list[Fixture]:
    if isinstance(data, dict):
        data = [data]

    fixtures = []

    for item in data:
        for match in item["matches"]:
            fixtures.append(
                Fixture(
                    id=match["id"],
                    name=f"{match['homeTeam']['shortName']} vs {match['awayTeam']['shortName']}",
                    competition=match["competition"]["name"],
                    competition_id=match["competition"]["id"],
                    homeTeam=match['homeTeam']['shortName'],
                    awayTeam=match['awayTeam']['shortName'],
                    homeTeamCrest=match['homeTeam']['crest'],
                    awayTeamCrest=match['awayTeam']['crest'],
                    matchday=match["matchday"],
                    score=f"{match['homeTeam']['shortName']}: {match['score']['fullTime']['home']} {match['awayTeam']['shortName']}: {match['score']['fullTime']['away']}",
                    winner=match['score']['winner'],
                    date=match["utcDate"],
                )
            )
    return (fixtures)

