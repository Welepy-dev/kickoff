from dataclasses import dataclass


@dataclass
class Fixture:
    id: int
    name: str
    competition: str
    competition_id: int
    awayTeam: str
    homeTeam: str
    matchweek: int
    homeTeamScore: int | None
    awayTeamScore: int | None
    score: str
    winner: str
    date: str
    fulltime: bool
    status: str


def _team_name(team: dict | None) -> str:
    """football-data may leave teams null for undecided cup ties."""
    if not team:
        return "TBD"
    return team.get("shortName") or team.get("name") or "TBD"


def parse_fixtures(data: list | dict | None) -> list[Fixture]:
    if not data:
        return []
    if isinstance(data, dict):
        data = [data]

    fixtures = []

    for item in data:
        if not item:
            continue
        for match in item.get("matches", []):
            score_obj = match.get("score") or {}
            full_time = score_obj.get("fullTime") or {}
            home_score = full_time.get("home")
            away_score = full_time.get("away")

            score = (
                f"{home_score} - {away_score}"
                if home_score is not None and away_score is not None
                else "-"
            )

            home_team = _team_name(match.get("homeTeam"))
            away_team = _team_name(match.get("awayTeam"))

            fixtures.append(
                Fixture(
                    id=match["id"],
                    name=f"{home_team} vs {away_team}",
                    competition=(match.get("competition") or {}).get("name", ""),
                    competition_id=(match.get("competition") or {}).get("id", 0),
                    homeTeam=home_team,
                    awayTeam=away_team,
                    matchweek=match.get("matchday", 0),
                    homeTeamScore=home_score,
                    awayTeamScore=away_score,
                    score=score,
                    winner=score_obj.get("winner") or "",
                    date=match.get("utcDate", ""),
                    fulltime=match.get("status") == "FINISHED",
                    status=match.get("status", ""),
                )
            )
    return fixtures
