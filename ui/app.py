from textual.app import App, ComposeResult
from textual.widgets import Label, Tabs, Tab, ContentSwitcher, ListView, ListItem
from textual.containers import Vertical, Horizontal

from api.endpoints import get_all_matches, get_all_top_scorers
from models.fixture import parse_fixtures
from models.scorer import parse_scorers
from ui.FixtureWidget import FixtureWidget

class UI(App):
    scorers = parse_scorers(get_all_top_scorers())



    CSS_PATH = "app.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        matches = parse_fixtures(get_all_matches())
        match = matches[0]
        yield Horizontal (
            Vertical (
                Label("Fixtures"),
                Tabs (
                    Tab("Next", id="firstTab"),
                    Tab("Previous", id="secondTab"),
                ),
                ContentSwitcher(
                    Vertical (
                        ListView (
                            ListItem(Label("Next placeholder 1")),
                            ListItem(Label("Next placeholder 2")),
                            ListItem(Label("Next placeholder 3")),
                            FixtureWidget("data", "hora", match.homeTeam, match.homeTeamCrest, match.awayTeam, match.awayTeamCrest, True, match.score),
                            id="next-list-1",
                        ),
                        id="firstTab",
                    ),
                    Vertical (
                        ListView (
                            ListItem(Label("Previous placeholder 1")),
                            ListItem(Label("Previous placeholder 2")),
                            ListItem(Label("Previous placeholder 3")),
                            id="previous-list-1",
                        ),
                        id="secondTab",
                    ),
                ),
                id="fixtures"
            ),
            Vertical (
                id="scorers"
            ),
            id="main"
        )

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.query_one(ContentSwitcher).current = event.tab.id

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
