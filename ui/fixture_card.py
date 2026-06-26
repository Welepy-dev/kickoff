from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label
from widgets import BigScore


class FixtureCard(Widget):
    can_focus = True

    def __init__(
        self,
        date_str: str,
        competition: str,
        matchweek: int,
        home_team: str,
        away_team: str,
        homeTeamScore: int,
        awayTeamScore: int,
        is_finished: bool,
        winner: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._date_str = date_str
        self._competition = competition
        self._matchweek = matchweek
        self._home_team = home_team
        self._away_team = away_team
        self._homeTeamScore = homeTeamScore
        self._awayTeamScore = awayTeamScore
        self._is_finished = is_finished
        self._winner = winner

    def _score_color(self) -> str:
        if self._winner == "DRAW":
            return "#f0c040"
        if self._winner in ("HOME_TEAM", "AWAY_TEAM"):
            return "#ff3b3b"
        return "#888888"

    def compose(self) -> ComposeResult:
        with Horizontal(classes="card-body"):
            with Vertical(classes="card-left"):
                yield Label(self._date_str, classes="card-date")
                yield Label(self._home_team, classes="card-home")
            with Horizontal(classes="card-center"):
                if self._is_finished and self._homeTeamScore is not None and self._awayTeamScore is not None:
                    yield BigScore(self._homeTeamScore, self._awayTeamScore, color=self._score_color(), classes="big-score")
                else:
                    yield Label("VS", classes="vs-label")
            with Vertical(classes="card-right"):
                yield Label(f"{self._competition} MatchDay {self._matchweek}", classes="card-week")
                yield Label(self._away_team, classes="card-away")

    def on_mount(self) -> None:
        if not self._is_finished:
            return
        home = self.query_one(".card-home", Label)
        away = self.query_one(".card-away", Label)
        if self._winner == "HOME_TEAM":
            home.add_class("winner")
            away.add_class("loser")
        elif self._winner == "AWAY_TEAM":
            home.add_class("loser")
            away.add_class("winner")
