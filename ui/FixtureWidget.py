from textual.containers import Horizontal, Vertical
from textual.widgets import Label
from textual.widget import Widget
from textual.app import ComposeResult

_widget_counter = 0

class FixtureWidget(Widget):
    def __init__(self, date: str, hour: str, homeTeam: str,
                 awayTeam: str, fullTime: bool, score: str, **kwargs):
        global _widget_counter
        _widget_counter += 1
        self._uid = _widget_counter
        super().__init__(**kwargs)
        self.date = date
        self.hour = hour
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.fullTime = fullTime
        self.score = score

    def compose(self) -> ComposeResult:
        middle_text = self.score if self.fullTime else self.hour
        yield Vertical(
            Horizontal(
                Label(str(self.date or "")),
                id=f"date_info_{self._uid}"
            ),
            Horizontal(
                Label(str(self.homeTeam or "")),
                Label(str(middle_text or "")),
                Label(str(self.awayTeam or "")),
                id=f"match_info_{self._uid}"
            )
        )
