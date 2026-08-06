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

from ui.leaguePopup import LeaguesPopup
from ui.fixture_list import PaginatedFixtureList
from api.endpoints import get_matches, get_standings, get_top_scorers
from models.standing import parse_standings
from models.fixture import parse_fixtures
from models.scorer import parse_scorers

from utils import get_competition_id
from ui.styles import (
    style_position,
    style_standing_team,
    style_stat,
    style_goal_diff,
    style_form,
    style_scorer_name,
    style_goals,
    style_assists,
    style_scorer_team,
)


class LeagueScreen(Screen):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "main_screen", "Go to main screen"),
        ("a", "show_leagues", "Show leagues")
    ]

    def __init__(self, league: str) -> None:
        super().__init__()
        self.league = league
        self.league_id = get_competition_id(league)

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
                        PaginatedFixtureList(id="next-fixtures"),
                        id="pane-next",
                    ),
                    Vertical(
                        PaginatedFixtureList(id="previous-fixtures"),
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
            "#", "Team", "MP", "W", "D", "L", "GD", "Last 5"
        )

        self.call_after_refresh(self.load_fixtures)
        self.call_after_refresh(self.load_standings)
        self.call_after_refresh(self.load_scorers)

    # ── standings ──────────────────────────────────────────────────────────

    @work(thread=True)
    def load_standings(self) -> None:
        try:
            data = get_standings(self.league_id)
        except Exception:
            self.app.call_from_thread(self._show_standings_error)
            return
        if not data:
            return
        standings = parse_standings(data)

        rows = []
        for s in standings:
            form_str = s.form or ""
            rows.append((
                style_position(s.position),
                style_standing_team(s.team, s.position),
                style_stat(s.playedGames),
                style_stat(s.wins),
                style_stat(s.draws),
                style_stat(s.losses),
                style_goal_diff(s.goalDifference),
                style_form(form_str),
            ))

        self.app.call_from_thread(self._populate_standings, rows)

    def _populate_standings(self, rows) -> None:
        self.query_one("#standings-table", DataTable).add_rows(rows)

    def _show_standings_error(self) -> None:
        self.query_one("#standings-table", DataTable).add_row(
            "Failed to load standings", "", "", "", "", "", "", ""
        )

    # ── fixtures ───────────────────────────────────────────────────────────

    @work(thread=True)
    def load_fixtures(self) -> None:
        try:
            data = get_matches(self.league_id)
        except Exception:
            self.app.call_from_thread(self._show_fixtures_error)
            return
        if not data:
            return
        now = datetime.now(timezone.utc)

        fixtures = parse_fixtures(data)
        fixtures = sorted(fixtures, key=attrgetter("date"))

        next_fixtures = []
        previous_fixtures = []

        for f in fixtures:
            dt = datetime.fromisoformat(f.date.replace("Z", "+00:00"))
            if f.fulltime or dt < now:
                previous_fixtures.insert(0, f)
            else:
                next_fixtures.append(f)

        self.app.call_from_thread(
            self._populate_fixtures, next_fixtures, previous_fixtures
        )

    def _populate_fixtures(self, next_fixtures, previous_fixtures) -> None:
        try:
            self.query_one("#loading").remove()
        except Exception:
            pass

        self.query_one("#next-fixtures", PaginatedFixtureList).load_fixtures(next_fixtures)
        self.query_one("#previous-fixtures", PaginatedFixtureList).load_fixtures(previous_fixtures)

    def _show_fixtures_error(self) -> None:
        try:
            self.query_one("#loading").remove()
        except Exception:
            pass
        self.query_one("#next-fixtures", PaginatedFixtureList).show_error(
            "Could not load fixtures"
        )

    # ── scorers ────────────────────────────────────────────────────────────

    @work(thread=True)
    def load_scorers(self) -> None:
        try:
            data = get_top_scorers(self.league_id)
        except Exception:
            self.app.call_from_thread(self._show_scorers_error)
            return
        if not data:
            return
        scorers = parse_scorers(data)
        scorers = sorted(scorers, key=attrgetter("goals"), reverse=True)

        rows = [
            (
                style_scorer_name(s.player, rank=i + 1),
                style_goals(s.goals),
                style_scorer_team(s.team),
                style_assists(s.assists),
            )
            for i, s in enumerate(scorers)
        ]

        self.app.call_from_thread(self._populate_scorers, rows)

    def _populate_scorers(self, rows) -> None:
        self.query_one("#scorers-table", DataTable).add_rows(rows)

    def _show_scorers_error(self) -> None:
        self.query_one("#scorers-table", DataTable).add_row(
            "Failed to load scorers", "-", "", ""
        )

    # ── actions ────────────────────────────────────────────────────────────

    def action_main_screen(self) -> None:
        self.dismiss()

    def action_show_leagues(self) -> None:
        self.app.push_screen(LeaguesPopup(), self.on_league_selected)

    def on_league_selected(self, league: str | None) -> None:
        if league:
            self.call_after_refresh(self.go_to_league, league)

    def go_to_league(self, league: str) -> None:
        self.dismiss()
        self.app.push_screen(LeagueScreen(league))

    def action_toggle_dark(self) -> None:
        self.app.theme = (
            "textual-dark"
            if self.app.theme == "textual-light"
            else "textual-light"
        )

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab.id == "tab-next":
            self.query_one(ContentSwitcher).current = "pane-next"
        elif event.tab.id == "tab-previous":
            self.query_one(ContentSwitcher).current = "pane-previous"
