from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Label


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

    def compose(self) -> ComposeResult:
        home_score = ""
        away_score = ""
        if self._is_finished:
            home_score = self._homeTeamScore
            away_score = self._awayTeamScore

        with Horizontal(classes="card-body"):
            with Vertical(classes="card-left"):
                yield Label(self._date_str, classes="card-date")
                yield Label(self._home_team, classes="card-home")
            with Horizontal(classes="card-center"):
                yield Label(home_score, classes="score-home")
                yield Label("VS", classes="vs-label")
                yield Label(away_score, classes="score-away")
            with Vertical(classes="card-right"):
                yield Label(f"{self._competition} MatchDay {self._matchweek}", classes="card-week")
                yield Label(self._away_team, classes="card-away")

    def on_mount(self) -> None:
        self._apply_result_classes()

    def _apply_result_classes(self):
        if not self._is_finished:
            return
        try:
            home = self.query_one(".card-home", Label)
            away = self.query_one(".card-away", Label)
            score_home = self.query_one(".score-home", Label)
            score_away = self.query_one(".score-away", Label)
        except NoMatches:
            return

        score_home.add_class("score")
        score_away.add_class("score")

        if self._winner == "DRAW":
            score_home.add_class("draw")
            score_away.add_class("draw")
        elif self._winner == "HOME_TEAM":
            score_home.add_class("finished")
            score_away.add_class("finished")
            home.add_class("winner")
            away.add_class("loser")
        elif self._winner == "AWAY_TEAM":
            score_home.add_class("finished")
            score_away.add_class("finished")
            home.add_class("loser")
            away.add_class("winner")
        else:
            score_home.add_class("finished")
            score_away.add_class("finished")
