from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Label

from models.fixture import Fixture
from ui.fixture_card import FixtureCard


class PaginatedFixtureList(Widget):
    DEFAULT_CSS = """
    PaginatedFixtureList {
        height: 1fr;
    }
    #cards-container {
        height: 1fr;
        overflow-y: auto;
    }
    #cards-container:empty {
        height: 1fr;
    }
    #pagination-bar {
        height: 3;
        align: center middle;
        margin: 0 1;
    }
    .page-btn {
        width: 10;
    }
    #page-info {
        width: auto;
        margin: 0 2;
        content-align: center middle;
    }
    #empty-label {
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
    }
    """

    PAGE_SIZE = 8

    def __init__(self, fixtures: list[Fixture] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._fixtures = fixtures or []
        self._current_page = 0

    @property
    def total_pages(self) -> int:
        return max(1, (len(self._fixtures) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)

    @property
    def _page_fixtures(self) -> list[Fixture]:
        start = self._current_page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        return self._fixtures[start:end]

    def compose(self) -> ComposeResult:
        yield Vertical(id="cards-container")
        yield Horizontal(
            Button("◀ Prev", id="prev-page", classes="page-btn"),
            Label("Page 1/1", id="page-info"),
            Button("Next ▶", id="next-page", classes="page-btn"),
            id="pagination-bar",
        )

    def on_mount(self) -> None:
        self._render_page()

    def load_fixtures(self, fixtures: list[Fixture]) -> None:
        self._fixtures = fixtures
        self._current_page = 0
        self._render_page()

    def _render_page(self) -> None:
        container = self.query_one("#cards-container", Vertical)
        container.remove_children()

        if not self._fixtures:
            container.mount(Label("No fixtures", id="empty-label"))
            self.query_one("#page-info", Label).update("Page 0/0")
            self._update_buttons()
            return

        for fixture in self._page_fixtures:
            dt = datetime.fromisoformat(fixture.date.replace("Z", "+00:00"))
            date_str = f"{dt.day:02d}/{dt.month:02d} {dt.hour:02d}:{dt.minute:02d}"
            card = FixtureCard(
                date_str=date_str,
                matchweek=fixture.matchday,
                home_team=fixture.homeTeam or "",
                away_team=fixture.awayTeam or "",
                score=fixture.score,
                is_finished=fixture.fulltime,
                winner=fixture.winner,
            )
            container.mount(card)

        self.query_one("#page-info", Label).update(
            f"Page {self._current_page + 1}/{self.total_pages}"
        )
        self._update_buttons()

    def _update_buttons(self) -> None:
        prev = self.query_one("#prev-page", Button)
        next_btn = self.query_one("#next-page", Button)
        prev.disabled = self._current_page == 0
        next_btn.disabled = self._current_page >= self.total_pages - 1

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "prev-page" and self._current_page > 0:
            self._current_page -= 1
            self._render_page()
        elif event.button.id == "next-page" and self._current_page < self.total_pages - 1:
            self._current_page += 1
            self._render_page()
