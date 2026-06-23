from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.containers import Grid

class LeaguesPopup(ModalScreen[str]):

    def compose(self) -> ComposeResult:
        yield Grid(
            Button("Champions League"),
            Button("Premier League"),
            Button("Primeira Liga"),
            Button("World Cup"),
            Button("Eredivisie"),
            Button("Bundesliga"),
            Button("Serie A"),
            Button("Euro"),
            Button("Ligue 1"),
            Button("Laliga"),
            id="leagueButtons"
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(str(event.button.label))
