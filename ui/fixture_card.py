from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Label


class FixtureCard(Widget):
    DEFAULT_CSS = """
    FixtureCard {
        border: solid $surface;
        height: 5;
        margin: 0 1 1 1;
        padding: 0 2;
    }
    .card-top {
        height: 1;
    }
    .card-date {
        width: 1fr;
        content-align: left middle;
        color: $text-muted;
    }
    .card-week {
        width: auto;
        content-align: right middle;
        color: $accent;
    }
    .card-center {
        height: 1;
        content-align: center middle;
    }
    .card-center.score {
        text-style: bold;
    }
    .card-center.draw {
        color: $warning;
    }
    .card-center.finished {
        color: $text;
    }
    .card-bottom {
        height: 1;
    }
    .card-home, .card-away {
        width: 1fr;
        text-style: bold;
    }
    .card-home {
        content-align: left middle;
    }
    .card-away {
        content-align: right middle;
    }
    .card-home.winner, .card-away.winner {
        color: $success;
    }
    .card-home.loser, .card-away.loser {
        color: $error;
    }
    """

    def __init__(
        self,
        date_str: str,
        matchweek: int,
        home_team: str,
        away_team: str,
        score: str = "-",
        is_finished: bool = False,
        winner: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._date_str = date_str
        self._matchweek = matchweek
        self._home_team = home_team
        self._away_team = away_team
        self._score = score
        self._is_finished = is_finished
        self._winner = winner

    def compose(self) -> ComposeResult:
        center_text = self._score if self._is_finished else "VS."

        yield Horizontal(
            Label(self._date_str, classes="card-date"),
            Label(f"MD{self._matchweek}", classes="card-week"),
            classes="card-top",
        )
        yield Label(center_text, classes="card-center")
        yield Horizontal(
            Label(self._home_team, classes="card-home"),
            Label(self._away_team, classes="card-away"),
            classes="card-bottom",
        )

    def on_mount(self) -> None:
        self._apply_result_classes()

    def _apply_result_classes(self):
        if not self._is_finished:
            return
        try:
            center = self.query_one(".card-center", Label)
            home = self.query_one(".card-home", Label)
            away = self.query_one(".card-away", Label)
        except NoMatches:
            return

        center.add_class("score")
        if self._winner == "DRAW":
            center.add_class("draw")
        elif self._winner in ("HOME_TEAM", "AWAY_TEAM"):
            center.add_class("finished")
            if self._winner == "HOME_TEAM":
                home.add_class("winner")
                away.add_class("loser")
            else:
                home.add_class("loser")
                away.add_class("winner")
        else:
            center.add_class("finished")
