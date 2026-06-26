from rich.style import Style
from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static

from bigscore import render_score


class BigScore(Static):
    """Textual widget that renders a live football score using the half-block font."""

    home: reactive[int] = reactive(0)
    away: reactive[int] = reactive(0)

    def __init__(self, home: int, away: int, color: str = "#ff3b3b", **kwargs) -> None:
        super().__init__(**kwargs)
        self.home = home
        self.away = away
        self._color = color

    def render(self) -> Text:
        raw = render_score(self.home, self.away)
        return Text(raw, style=Style(color=self._color, bold=True))

    def watch_home(self, _: int) -> None:
        self.refresh()

    def watch_away(self, _: int) -> None:
        self.refresh()
