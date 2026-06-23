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

class UI(App):

    CSS_PATH = "app.css"

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
                        DataTable(id="next-table", cursor_type="row"),
                        id="pane-next"
                    ),
                    Vertical(
                        DataTable(id="previous-table", cursor_type="row"),
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
        for table_id in ("next-table", "previous-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns("Date", "Home", "Score", "Away", "Competition", "Time")
        self.call_after_refresh(self.load_fixtures)
        self.call_after_refresh(self.load_scorers)

    @work(thread=True)
    def load_scorers(self) -> None:
        scorers = parse_scorers(get_all_top_scorers())

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
