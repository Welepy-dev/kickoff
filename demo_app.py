from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Label

from widgets import BigScore


class ScoreboardApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    #board {
        width: auto;
        height: auto;
        align: center middle;
        padding: 1 2;
        border: solid $surface;
    }
    #teams {
        layout: horizontal;
        width: auto;
        height: auto;
        content-align: center middle;
        margin-bottom: 1;
    }
    #home-label {
        width: 1fr;
        content-align: right middle;
        text-style: bold;
        padding-right: 4;
    }
    #away-label {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
        padding-left: 4;
    }
    BigScore {
        width: auto;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("h", "score_home", "Home +1"),
        Binding("a", "score_away", "Away +1"),
        Binding("r", "reset", "Reset"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="board"):
            yield Label("[b]Home[/b]  vs  [b]Away[/b]", id="teams")
            yield BigScore(0, 0, id="score")
        yield Footer()

    def action_score_home(self) -> None:
        widget = self.query_one("#score", BigScore)
        widget.home += 1

    def action_score_away(self) -> None:
        widget = self.query_one("#score", BigScore)
        widget.away += 1

    def action_reset(self) -> None:
        widget = self.query_one("#score", BigScore)
        widget.home = 0
        widget.away = 0


if __name__ == "__main__":
    ScoreboardApp().run()
