from dataclasses import dataclass

@dataclass
class Fixture:
    id: int
    name: str
    competition: str
    competition_id: str
    awayTeam: str
    homeTeam: str
    matchweek: int
    homeTeamScore: int
    awayTeamScore: int
    score: str
    winner: str
    date: str
    fulltime: bool

def parse_fixtures(data: list | dict) -> list[Fixture]:
    if isinstance(data, dict):
        data = [data]

    fixtures = []

    for item in data:
        for match in item["matches"]:
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']

            score = (
                f"{home_score} - {away_score}"
                if home_score is not None and away_score is not None
                else "-"
            )

            home_short = match['homeTeam']['shortName'] or match['homeTeam'].get('name', 'Unknown')
            away_short = match['awayTeam']['shortName'] or match['awayTeam'].get('name', 'Unknown')

            fixtures.append(
                Fixture(
                    id=match["id"],
                    name=f"{home_short} vs {away_short}",
                    competition=match["competition"]["name"],
                    competition_id=match["competition"]["id"],
                    homeTeam=home_short,
                    awayTeam=away_short,
                    matchweek=match["matchday"],
                    homeTeamScore=match['score']['fullTime']['home'],
                    awayTeamScore=match['score']['fullTime']['away'],
                    score=score,
                    winner=match['score']['winner'] or '',
                    date=match["utcDate"],
                    fulltime=True if match['status'] == 'FINISHED' else False
                )
            )
    return fixtures
