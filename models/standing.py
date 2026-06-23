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

def parse_standings(data: list | dict) -> list[Standing]:
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]
    standings = []
    for item in data:
        for table in item["standings"]:
            if table["type"] != "TOTAL":
                continue
            for row in table["table"]:
                standings.append(
                    Standing(
                        team=row["team"]["shortName"],
                        team_id=row["team"]["id"],
                        competition=item["competition"]["name"],
                        competition_id=item["competition"]["id"],
                        playedGames=row["playedGames"],
                        wins=row["won"],
                        draws=row["draw"],
                        losses=row["lost"],
                        goalDifference=row["goalDifference"],
                        goalsFor=row["goalsFor"],
                        points=row["points"],
                        position=row["position"],
                    )
                )
    return standings
