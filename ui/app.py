from operator import attrgetter
from datetime import datetime, timezone
from api.endpoints import get_all_matches, get_all_top_scorers
from models.fixture import parse_fixtures
from models.scorer import parse_scorers

from textual.app import App, ComposeResult
from textual.widgets import Label, Tabs, Tab, ContentSwitcher, DataTable, LoadingIndicator, Footer
from textual.containers import Vertical, Horizontal
from textual import work
from ui.leaguePopup import LeaguesPopup
from ui.leagueScreen import LeagueScreen
from ui.fixture_list import PaginatedFixtureList

class UI(App):

    CSS_PATH = [
        "styles/app.css",
        "styles/fixture_card.css",
        "styles/fixture_list.css",
        "styles/league_popup.css",
    ]

    BINDINGS = [ 
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "show_leagues", "Show leagues")
    ]

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Label("Fixtures"),
                Tabs(
                    Tab("Next", id="tab-next"),
                    Tab("Previous", id="tab-previous"),
                ),
                ContentSwitcher(
                    Vertical(
                        LoadingIndicator(id="loading"),
                        PaginatedFixtureList(id="next-fixtures"),
                        id="pane-next"
                    ),
                    Vertical(
                        PaginatedFixtureList(id="previous-fixtures"),
                        id="pane-previous"
                    ),
                    initial="pane-next"
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
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#scorers-table", DataTable).add_columns("Name", "Goals", "Team", "Assists")
        self.call_after_refresh(self.load_fixtures)
        self.call_after_refresh(self.load_scorers)

    @work(thread=True)
    def load_scorers(self) -> None:
        try:
            scorers = parse_scorers(get_all_top_scorers())
        except Exception:
            self.app.call_from_thread(self._show_scorers_error)
            return

        # Merge duplicate players across competitions
        merged: dict[str, dict] = {}
        for scorer in scorers:
            key = scorer.player.strip().lower()
            if key in merged:
                merged[key]["goals"] += scorer.goals or 0
                merged[key]["assists"] += scorer.assists or 0
                # Append team if not already listed
                if scorer.team not in merged[key]["teams"]:
                    merged[key]["teams"].append(scorer.team)
            else:
                merged[key] = {
                    "player": scorer.player,
                    "goals": scorer.goals or 0,
                    "assists": scorer.assists or 0,
                    "teams": [scorer.team],
                }

        # Build rows sorted by goals descending
        scorer_rows = sorted(
            merged.values(), key=lambda s: s["goals"], reverse=True
        )
        rows = [
            (
                entry["player"],
                entry["goals"],
                " / ".join(entry["teams"]),  # e.g. "Man City / England"
                entry["assists"],
            )
            for entry in scorer_rows
        ]

        self.app.call_from_thread(self._populate_scorers, rows)

    def _populate_scorers(self, scorer_rows) -> None:
        self.query_one("#scorers-table", DataTable).add_rows(scorer_rows)

    def _show_scorers_error(self) -> None:
        self.query_one("#scorers-table", DataTable).add_row(
            "Failed to load scorers", "-", "", ""
        )

    @work(thread=True)
    def load_fixtures(self) -> None:
        try:
            fixtures = parse_fixtures(get_all_matches())
        except Exception:
            self.app.call_from_thread(self._show_fixtures_error)
            return

        now = datetime.now(timezone.utc)
        fixtures = sorted(fixtures, key=attrgetter('date'))

        next_fixtures = []
        previous_fixtures = []

        for fixture in fixtures:
            dt = datetime.fromisoformat(fixture.date.replace("Z", "+00:00"))
            if fixture.fulltime or dt < now:
                previous_fixtures.insert(0, fixture)
            else:
                next_fixtures.append(fixture)

        self.app.call_from_thread(self._populate_tables, next_fixtures, previous_fixtures)

    def _show_fixtures_error(self) -> None:
        try:
            self.query_one("#loading").remove()
        except Exception:
            pass
        self.query_one("#next-fixtures", PaginatedFixtureList).show_error(
            "Could not load fixtures"
        )

    def _populate_tables(self, next_fixtures, previous_fixtures) -> None:
        try:
            self.query_one("#loading").remove()
        except Exception:
            pass

        self.query_one("#next-fixtures", PaginatedFixtureList).load_fixtures(next_fixtures)
        self.query_one("#previous-fixtures", PaginatedFixtureList).load_fixtures(previous_fixtures)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab.id == "tab-next":
            self.query_one(ContentSwitcher).current = "pane-next"
        elif event.tab.id == "tab-previous":
            self.query_one(ContentSwitcher).current = "pane-previous"

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    def action_show_leagues(self) -> None:
        self.push_screen(LeaguesPopup(), self.on_league_selected)

    def on_league_selected(self, league: str | None) -> None:
        if league:
            self.call_after_refresh(self.go_to_league, league)

    def go_to_league(self, league: str) -> None:
        self.push_screen(LeagueScreen(league))
