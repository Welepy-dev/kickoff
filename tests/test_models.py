import pytest

from models.fixture import parse_fixtures
from models.standing import parse_standings
from models.scorer import parse_scorers
from utils import get_competition_id, parse_utc


# ── fixtures ────────────────────────────────────────────────────────────────

def test_finished_fixture():
    data = {
        "matches": [
            {
                "id": 2,
                "status": "FINISHED",
                "score": {"fullTime": {"home": 2, "away": 1}, "winner": "HOME_TEAM"},
                "homeTeam": {"shortName": "ARS", "name": "Arsenal"},
                "awayTeam": {"shortName": "CHE", "name": "Chelsea"},
                "matchday": 3,
                "competition": {"name": "Premier League", "id": 2021},
                "utcDate": "2026-08-05T19:00:00Z",
            }
        ]
    }
    fx = parse_fixtures(data)
    assert len(fx) == 1
    f = fx[0]
    assert f.homeTeam == "ARS"
    assert f.awayTeam == "CHE"
    assert f.score == "2 - 1"
    assert f.fulltime is True
    assert f.status == "FINISHED"
    assert f.competition_id == 2021


def test_postponed_match_with_null_score_and_teams():
    data = {
        "matches": [
            {
                "id": 1,
                "status": "POSTPONED",
                "score": None,
                "homeTeam": None,
                "awayTeam": None,
                "matchday": 3,
                "competition": {"name": "UCL", "id": 2001},
                "utcDate": "2026-08-06T19:00:00Z",
            }
        ]
    }
    fx = parse_fixtures(data)
    assert len(fx) == 1
    f = fx[0]
    assert f.homeTeam == "TBD"
    assert f.awayTeam == "TBD"
    assert f.score == "-"
    assert f.fulltime is False
    assert f.status == "POSTPONED"


def test_parse_fixtures_skips_failed_batch_entries():
    assert parse_fixtures([None, {"matches": []}]) == []
    assert parse_fixtures(None) == []


def test_parse_fixtures_handles_dict_wrapping():
    fx = parse_fixtures({"matches": []})
    assert fx == []


# ── standings ────────────────────────────────────────────────────────────────

def test_standings_parse_form():
    data = {
        "competition": {"name": "Premier League", "id": 2021},
        "standings": [
            {
                "type": "TOTAL",
                "table": [
                    {
                        "position": 1,
                        "team": {"shortName": "LIV", "name": "Liverpool"},
                        "playedGames": 5,
                        "won": 4,
                        "draw": 1,
                        "lost": 0,
                        "goalDifference": 9,
                        "goalsFor": 12,
                        "points": 13,
                        "form": "WWDLW",
                    }
                ],
            }
        ],
    }
    st = parse_standings(data)
    assert len(st) == 1
    assert st[0].form == "WWDLW"
    assert st[0].points == 13


def test_standings_ignores_non_total_tables():
    data = {
        "standings": [
            {"type": "HOME", "table": [{"team": {"shortName": "ARS"}}]},
            {"type": "TOTAL", "table": [{"team": {"shortName": "MCI"}, "position": 1}]},
        ]
    }
    st = parse_standings(data)
    assert len(st) == 1
    assert st[0].team == "MCI"


def test_standings_empty():
    assert parse_standings(None) == []
    assert parse_standings({}) == []


# ── scorers ──────────────────────────────────────────────────────────────────

def test_scorers_missing_optional_fields():
    data = {
        "scorers": [
            {
                "player": {"id": 1, "name": "Player One"},
                "goals": 5,
                "team": {"shortName": "TOT"},
            }
        ]
    }
    s = parse_scorers(data)
    assert len(s) == 1
    assert s[0].assists == 0
    assert s[0].penalties == 0
    assert s[0].nationality == ""
    assert s[0].team == "TOT"
    assert s[0].gamesPlayed == 0


def test_scorers_skip_failed_entries():
    assert parse_scorers([None, {"scorers": []}]) == []
    assert parse_scorers(None) == []


# ── utils ────────────────────────────────────────────────────────────────────

def test_parse_utc():
    dt = parse_utc("2026-08-06T19:00:00Z")
    assert dt is not None
    assert dt.tzinfo is not None
    assert parse_utc("") is None
    assert parse_utc("not-a-date") is None
    assert parse_utc(None) is None


def test_get_competition_id():
    assert get_competition_id("Premier League") == 2021
    assert get_competition_id("Champions League") == 2001
    with pytest.raises(ValueError):
        get_competition_id("Unknown League")
