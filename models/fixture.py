from dataclasses import dataclass
from datetime import datetime, timedelta

from utils import parse_utc

LIVE_STATUSES = {"IN_PLAY", "PAUSED", "LIVE"}
_NOT_STARTED = {"SCHEDULED", "TIMED"}
# Cached data can lag behind reality: a match still marked SCHEDULED shortly
# after kickoff is most likely being played, so keep it in "next".
_KICKOFF_GRACE = timedelta(hours=3)


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

    @property
    def live(self) -> bool:
        return self.status in LIVE_STATUSES


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


def split_fixtures(
    fixtures: list[Fixture], now: datetime
) -> tuple[list[Fixture], list[Fixture]]:
    """Split fixtures into (next, previous).

    Next: live matches, then upcoming ones by kickoff, undated ones last.
    Previous: finished or past-dated matches (incl. postponed), newest first.
    """
    next_fixtures = []
    previous_fixtures = []
    for fixture in fixtures:
        dt = parse_utc(fixture.date)
        if fixture.fulltime:
            previous_fixtures.append((fixture, dt))
        elif fixture.live or dt is None or dt >= now:
            next_fixtures.append((fixture, dt))
        elif fixture.status in _NOT_STARTED and dt >= now - _KICKOFF_GRACE:
            next_fixtures.append((fixture, dt))
        else:
            previous_fixtures.append((fixture, dt))

    next_fixtures.sort(key=lambda p: (not p[0].live, p[1] is None, p[1] or now))
    previous_fixtures.sort(key=lambda p: (p[1] is not None, p[1] or now), reverse=True)
    return [f for f, _ in next_fixtures], [f for f, _ in previous_fixtures]
