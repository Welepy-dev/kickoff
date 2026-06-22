from operator import attrgetter
from datetime import datetime, timezone

from textual import work
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Label,
    Tabs,
    ContentSwitcher,
    Tab,
    LoadingIndicator,
    DataTable,
    Footer,
)

from api.endpoints import get_matches, get_standings, get_top_scorers
from models.standing import parse_standings
from models.fixture import parse_fixtures
from models.scorer import parse_scorers
from utils import get_competition_id


class LeagueScreen(Screen):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "main_screen", "Go to main screen"),
    ]

    def __init__(self, league: str) -> None:
        super().__init__()
        self.league = league
        self.league_id = get_competition_id(league)
        print(self.league)

    def compose(self):
        yield Label(self.league)

        yield Horizontal(
            # Fixtures
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
                        id="pane-next",
                    ),
                    Vertical(
                        DataTable(id="previous-table", cursor_type="row"),
                        id="pane-previous",
                    ),
                    initial="pane-next",
                ),
                id="fixtures",
            ),

            Vertical(
                Label("Standings"),
                DataTable(id="standings-table", cursor_type="row"),
                id="standings",
            ),

            Vertical(
                Label("Top Scorers"),
                DataTable(id="scorers-table", cursor_type="row"),
                id="scorers",
            ),
        )

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#scorers-table", DataTable).add_columns(
            "Name", "Goals", "Team", "Assists"
        )

        self.query_one("#standings-table", DataTable).add_columns(
            "Team", "MP", "W", "D", "L", "DIFF", "Last 5"
        )

        for table_id in ("next-table", "previous-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns(
                "Date", "Home", "Score", "Away", "Competition", "Time"
            )

        # Load data safely
        self.call_after_refresh(self.load_fixtures)
        self.call_after_refresh(self.load_standings)
        self.call_after_refresh(self.load_scorers)

    @work(thread=True)
    def load_standings(self) -> None:
        standings = parse_standings(get_standings(self.league_id))

        rows = [
            (
                s.team,
                s.playedGames,
                s.wins,
                s.draws,
                s.losses,
                s.goalDifference,
                " ".join(getattr(s, "form", []) or []),
            )
            for s in standings
        ]

        self.app.call_from_thread(self._populate_standings, rows)

    def _populate_standings(self, rows) -> None:
        self.query_one("#standings-table", DataTable).add_rows(rows)

    @work(thread=True)
    def load_fixtures(self) -> None:
        now = datetime.now(timezone.utc)

        fixtures = parse_fixtures(get_matches(self.league_id))
        fixtures = sorted(fixtures, key=attrgetter("date"))

        next_rows = []
        previous_rows = []

        for f in fixtures:
            dt = datetime.fromisoformat(f.date.replace("Z", "+00:00"))

            row = (
                f"{dt.day:02d}/{dt.month:02d}",
                f.homeTeam or "",
                f.score,
                f.awayTeam or "",
                f.competition or "",
                str(dt.time()),
            )

            if f.fulltime or dt < now:
                previous_rows.insert(0, row)
            else:
                next_rows.append(row)

        self.app.call_from_thread(
            self._populate_fixtures, next_rows, previous_rows
        )

    def _populate_fixtures(self, next_rows, previous_rows) -> None:
        try:
            self.query_one("#loading").remove()
        except Exception:
            pass

        self.query_one("#next-table", DataTable).add_rows(next_rows)
        self.query_one("#previous-table", DataTable).add_rows(previous_rows)

    @work(thread=True)
    def load_scorers(self) -> None:
        scorers = parse_scorers(get_top_scorers(self.league_id))
        scorers = sorted(scorers, key=attrgetter("goals"), reverse=True)

        rows = [
            (s.player, s.goals, s.team, s.assists)
            for s in scorers
        ]

        self.app.call_from_thread(self._populate_scorers, rows)

    def _populate_scorers(self, rows) -> None:
        self.query_one("#scorers-table", DataTable).add_rows(rows)

    def action_main_screen(self) -> None:
        self.dismiss()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark"
            if self.theme == "textual-light"
            else "textual-light"
        )

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab.id == "tab-next":
            self.query_one(ContentSwitcher).current = "pane-next"
        elif event.tab.id == "tab-previous":
            self.query_one(ContentSwitcher).current = "pane-previous"
