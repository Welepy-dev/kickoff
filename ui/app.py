from operator import attrgetter
from datetime import datetime, timezone
from api.endpoints import get_all_matches, get_all_top_scorers
from models.fixture import parse_fixtures
from models.scorer import parse_scorers
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
                        DataTable(id="next-table", cursor_type="row"),
                        id="firstTab"
                    ),
                    Vertical(
                        DataTable(id="previous-table", cursor_type="row"),
                        id="secondTab"
                    ),
                ),
                id="fixtures"
            ),
            Vertical(
                Label("Top Scorers"),
                DataTable(id="scorers-table", cursor_type="row"),
                id="scorers"
            ),
            id="main"
        )

    def on_mount(self) -> None:
        self.query_one("#scorers-table", DataTable).add_columns("Name", "Goals", "Team", "Assists")
        for table_id in ("next-table", "previous-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns("Date", "Home", "Score", "Away", "Competition", "Time")
        self.load_fixtures()
        self.load_scorers()

    @work(thread=True)
    def load_scorers(self) -> None:
        scorers = parse_scorers(get_all_top_scorers())
        scorers = sorted(scorers, key=attrgetter('goals'), reverse=True)

        scorer_rows = []

        for scorer in scorers:
            row = (
                scorer.player,
                scorer.goals,
                scorer.team,
                scorer.assists
            )
            scorer_rows.append(row)
        self.app.call_from_thread(self._populate_scorers, scorer_rows)

    def _populate_scorers(self, scorer_rows) -> None:
        self.query_one("#scorers-table", DataTable).add_rows(scorer_rows)


    @work(thread=True)
    def load_fixtures(self) -> None:
        now = datetime.now(timezone.utc)
        fixtures = parse_fixtures(get_all_matches())
        fixtures = sorted(fixtures, key=attrgetter('date'))

        next_rows = []
        previous_rows = []

        for fixture in fixtures:
            dt = datetime.fromisoformat(fixture.date.replace("Z", "+00:00"))
            middle = fixture.score
            row = (
                f"{dt.day:02d}/{dt.month:02d}",
                fixture.homeTeam or "",
                middle,
                fixture.awayTeam or "",
                fixture.competition or "",
                str(dt.time()),
            )
            if fixture.fulltime or dt < now:
                previous_rows.insert(0, row)
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
