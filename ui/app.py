from textual.app import App, ComposeResult
from textual.widgets import Label, Tabs, Tab, ContentSwitcher
from textual.containers import Vertical, Horizontal


class UI(App):
    
    CSS_PATH = "app.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Horizontal (
            Vertical (
                Label ("Fixtures"),
                Tabs (
                    Tab("Next", id="firstTab"),
                    Tab("Previous", id="secondTab"),
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
