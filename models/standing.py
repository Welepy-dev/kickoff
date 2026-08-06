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
    form: str


def parse_standings(data: list | dict | None) -> list[Standing]:
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]
    standings = []
    for item in data:
        if not item:
            continue
        for table in item.get("standings") or []:
            if table.get("type") != "TOTAL":
                continue
            for row in table.get("table", []):
                team = row.get("team") or {}
                standings.append(
                    Standing(
                        team=team.get("shortName") or team.get("name") or "TBD",
                        team_id=team.get("id", 0),
                        competition=(item.get("competition") or {}).get("name", ""),
                        competition_id=(item.get("competition") or {}).get("id", 0),
                        playedGames=row.get("playedGames", 0),
                        wins=row.get("won", 0),
                        draws=row.get("draw", 0),
                        losses=row.get("lost", 0),
                        goalDifference=row.get("goalDifference", 0),
                        goalsFor=row.get("goalsFor", 0),
                        points=row.get("points", 0),
                        position=row.get("position", 0),
                        form=row.get("form") or "",
                    )
                )
    return standings
