from textual.containers import Horizontal
from textual.widgets import Label
from textual.widget import Widget
from textual.app import ComposeResult

from rich_pixels import Pixels
from PIL import Image as PILImage
import requests
from io import BytesIO

class BadgeWidget(Widget):
    def __init__(self, url: str, size: tuple = (4, 4), **kwargs):
        super().__init__(**kwargs)
        response = requests.get(url)
        img = PILImage.open(BytesIO(response.content)).resize(size)
        self._pixels = Pixels.from_image(img)

    def render(self):
        return self._pixels

class FixtureWidget(Widget):
    def __init__(self, date: str, hour: str, homeTeam: str, homeTeamBadgeURL: str,
                 awayTeam: str, awayTeamBadgeURL: str, fullTime: bool, result: str, **kwargs):
        super().__init__(**kwargs)
        self.date = date
        self.hour = hour
        self.homeTeam = homeTeam
        self.homeTeamBadgeURL = homeTeamBadgeURL
        self.awayTeam = awayTeam
        self.awayTeamBadgeURL = awayTeamBadgeURL
        self.fullTime = fullTime
        self.result = result

    def compose(self) -> ComposeResult:
        middle_label = Label(self.hour) if not self.fullTime else Label(self.result)
        yield Horizontal(
            BadgeWidget(self.homeTeamBadgeURL, size=(4, 4)),
            Label(self.homeTeam),
            middle_label,
            Label(self.awayTeam),
            BadgeWidget(self.awayTeamBadgeURL, size=(4, 4)),
        )
# from io import BytesIO

# import requests
# from PIL import Image
# from rich_pixels import Pixels

# from textual.containers import Horizontal
# from textual.widgets import Label, Static
# from textual.widget import Widget
# from textual.app import ComposeResult

# class UserCard(Widget):
#     def __init__(self, date: str, hour: str, homeTeam: str, homeTeamBadgeURL: str,
#                  awayTeam: str, awayTeamBadgeURL: str, fullTime: bool, result: str, **kwargs):
#         super().__init__(**kwargs)
#         self.date = date
#         self.hour = hour
#         self.homeTeam = homeTeam
#         self.homeTeamBadgeURL = homeTeamBadgeURL
#         self.awayTeam = awayTeam
#         self.awayTeamBadgeURL = awayTeamBadgeURL
#         self.fullTime = fullTime
#         self.result = result

#     def compose(self) -> ComposeResult:
#         middle_label = Label(self.hour) if not self.fullTime else Label(self.result)

#         yield Horizontal(
#             Horizontal(
#                 Label(self.date),
#             ),
#             Label(self.homeTeam),
#             Static(self._badge_renderable(self.homeTeamBadgeURL), shrink=True),
#             middle_label,
#             Static(self._badge_renderable(self.awayTeamBadgeURL), shrink=True),
#             Label(self.awayTeam),
#         )

#     def _badge_renderable(self, image_url: str):
#         response = requests.get(image_url, timeout=10)
#         response.raise_for_status()

#         with Image.open(BytesIO(response.content)) as image:
#             image = image.convert("RGBA")
#             image.thumbnail((24, 24))
#             return Pixels.from_image(image)

