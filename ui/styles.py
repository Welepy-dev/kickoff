"""
Rich styling helpers for the football TUI.
Colors drawn from the koda.nvim dark palette:
  fg      #c8c0b0  warm off-white
  fg_dim  #6e6860  muted secondary
  sky     #6e8fa8  accent / headers
  green   #7a9e7e  win / positive
  amber   #b89a6a  draw / neutral
  rose    #a06060  loss / negative
"""

from rich.text import Text


# ── palette ──────────────────────────────────────────────────────────────────

FG      = "#c8c0b0"
FG_DIM  = "#6e6860"
SKY     = "#6e8fa8"
GREEN   = "#7a9e7e"
AMBER   = "#b89a6a"
ROSE    = "#a06060"


# ── fixtures / matches ────────────────────────────────────────────────────────

def style_date(date: str) -> Text:
    """Dim date column — it's context, not the focus."""
    return Text(date, style=f"{FG_DIM}")


def style_team(name: str, is_winner: bool = False, is_loser: bool = False) -> Text:
    """
    Team name: bold+green for winner, rose for loser, plain fg for draw/upcoming.
    """
    if is_winner:
        return Text(name, style=f"bold {GREEN}")
    if is_loser:
        return Text(name, style=ROSE)
    return Text(name, style=FG)


def style_score(score: str, winner: str, home_team: str) -> Text:
    """
    Finished match: colour the score based on outcome.
    Upcoming match ("-"): muted.
    """
    if score == "-":
        return Text(score, style=FG_DIM)

    # winner is "HOME_TEAM", "AWAY_TEAM", "DRAW", or ""
    if winner == "DRAW":
        return Text(score, style=AMBER)
    elif winner in ("HOME_TEAM", "AWAY_TEAM"):
        return Text(score, style=f"bold {GREEN}")
    return Text(score, style=FG)


def style_competition(name: str) -> Text:
    """Competition name — subtle accent colour."""
    return Text(name, style=SKY)


def style_time(time_str: str) -> Text:
    """Match time — dimmed, purely informational."""
    return Text(time_str, style=FG_DIM)


# ── standings ─────────────────────────────────────────────────────────────────

def style_position(pos: int) -> Text:
    """Top 4 in sky (Champions League spots), bottom 3 in rose (relegation)."""
    if pos <= 4:
        return Text(str(pos), style=f"bold {SKY}")
    if pos >= 18:
        return Text(str(pos), style=ROSE)
    return Text(str(pos), style=FG_DIM)


def style_standing_team(name: str, pos: int) -> Text:
    """Bold for CL positions, rose for relegation, normal otherwise."""
    if pos <= 4:
        return Text(name, style=f"bold {FG}")
    if pos >= 18:
        return Text(name, style=ROSE)
    return Text(name, style=FG)


def style_stat(value: int | str) -> Text:
    """Generic stat number — plain fg."""
    return Text(str(value), style=FG)


def style_goal_diff(diff: int) -> Text:
    """Positive diff in green, negative in rose, zero dimmed."""
    if diff > 0:
        return Text(f"+{diff}", style=GREEN)
    if diff < 0:
        return Text(str(diff), style=ROSE)
    return Text("0", style=FG_DIM)


def style_form(form_str: str | list) -> Text:
    """
    Render a form string like "WWDLW" or "W W D L W" with per-character colour.
    Accepts a compact string, a space-joined string, or a list of tokens.
    """
    result = Text()
    if isinstance(form_str, str):
        tokens = list(form_str) if " " not in form_str else form_str.split()
    else:
        tokens = form_str
    for token in tokens:
        if token == "W":
            result.append("W ", style=f"bold {GREEN}")
        elif token == "L":
            result.append("L ", style=ROSE)
        elif token == "D":
            result.append("D ", style=AMBER)
        else:
            result.append(f"{token} ", style=FG_DIM)
    return result


# ── scorers ───────────────────────────────────────────────────────────────────

def style_scorer_name(name: str, rank: int) -> Text:
    """Top scorer gets a sky highlight."""
    if rank == 1:
        return Text(name, style=f"bold {SKY}")
    return Text(name, style=FG)


def style_goals(goals: int) -> Text:
    """Goal tally — bold green for top scorers, dimmer as it drops."""
    if goals >= 20:
        return Text(str(goals), style=f"bold {GREEN}")
    if goals >= 10:
        return Text(str(goals), style=GREEN)
    return Text(str(goals), style=FG)


def style_assists(assists: int) -> Text:
    if assists and assists > 0:
        return Text(str(assists), style=AMBER)
    return Text(str(assists or 0), style=FG_DIM)


def style_scorer_team(name: str) -> Text:
    return Text(name, style=FG_DIM)
