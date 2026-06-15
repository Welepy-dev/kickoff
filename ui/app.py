from datetime import datetime, timezone
from api.endpoints import get_all_matches
from models.fixture import parse_fixtures
from textual.app import App, ComposeResult
from textual.widgets import Label, Tabs, Tab, ContentSwitcher, DataTable, LoadingIndicator
from textual.containers import Vertical, Horizontal
from textual import work

class UI(App):

    CSS_PATH = "app.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Label("Fixtures"),
                Tabs(
                    Tab("Next", id="firstTab"),
                    Tab("Previous", id="secondTab"),
                ),
                ContentSwitcher(
                    Vertical(
                        LoadingIndicator(id="loading"),
                        DataTable(id="next-table", show_cursor=False),
                        id="firstTab"
                    ),
                    Vertical(
                        DataTable(id="previous-table", show_cursor=False),
                        id="secondTab"
                    ),
                ),
                id="fixtures"
            ),
            Vertical(id="scorers"),
            id="main"
        )

    def on_mount(self) -> None:
        for table_id in ("next-table", "previous-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns("Date", "Home", "Score / Time", "Away", "Competition")
        self.load_fixtures()

    @work(thread=True)
    def load_fixtures(self) -> None:
        now = datetime.now(timezone.utc)
        fixtures = parse_fixtures(get_all_matches())

        next_rows = []
        previous_rows = []

        for fixture in fixtures:
            dt = datetime.fromisoformat(fixture.date.replace("Z", "+00:00"))
            middle = fixture.score if fixture.fulltime else f"{dt.hour:02d}:{dt.minute:02d}"
            row = (
                f"{dt.day:02d}/{dt.month:02d}",
                fixture.homeTeam or "",
                middle,
                fixture.awayTeam or "",
                fixture.competition or "",
            )
            if fixture.fulltime or dt < now:
                previous_rows.append(row)
            else:
                next_rows.append(row)

        self.app.call_from_thread(self._populate_tables, next_rows, previous_rows)

    def _populate_tables(self, next_rows, previous_rows) -> None:
        try:
            self.query_one("#loading").remove()
        except Exception:
            pass

        self.query_one("#next-table", DataTable).add_rows(next_rows)
        self.query_one("#previous-table", DataTable).add_rows(previous_rows)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        self.query_one(ContentSwitcher).current = event.tab.id

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
