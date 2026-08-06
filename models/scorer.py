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


def parse_scorers(data: list | dict | None) -> list[Scorer]:
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]

    scorers = []

    for item in data:
        if not item:
            continue
        for player in item.get("scorers", []):
            player_info = player.get("player") or {}
            team_info = player.get("team") or {}
            scorers.append(
                Scorer(
                    id=player_info.get("id", 0),
                    player=player_info.get("name") or "Unknown",
                    gamesPlayed=player.get("playedMatches", 0),
                    goals=player.get("goals", 0),
                    penalties=player.get("penalties", 0),
                    assists=player.get("assists", 0),
                    competition=(item.get("competition") or {}).get("name", ""),
                    competition_id=(item.get("competition") or {}).get("id", 0),
                    nationality=player_info.get("nationality") or "",
                    team=team_info.get("shortName") or team_info.get("name") or "TBD",
                    teamId=team_info.get("id", 0),
                )
            )
    return scorers
