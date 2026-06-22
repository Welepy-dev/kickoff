from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.containers import Grid

class LeaguesPopup(ModalScreen):

    def compose(self) -> ComposeResult:
        yield Grid(
            Button("Champions League"),
            Button("Europa League"),
            Button("Premier League"),
            Button("Primeira Liga"),
            Button("World Cup"),
            Button("Eredivisie"),
            Button("Bundesliga"),
            Button("Serie A"),
            Button("Ligue 1"),
            Button("Laliga"),
            id="leagueButtons"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.label)

    def menu_result(self, result) -> None:
        self.noify(f"Selected: {result}")
