"""
Half-block terminal font for rendering football scores.

Each digit is a 3-row glyph built from Unicode half-block characters
(█ FULL BLOCK U+2588, ▀ UPPER HALF BLOCK U+2580).  When printed in a
monospace terminal, adjacent glyphs tile seamlessly to form large numbers.

Assumption: the terminal must use a monospace font where every code point
is exactly one cell wide (standard CJK terminals may differ).
"""

GLYPHS: dict[str, list[str]] = {
    "0": ["█▀█", "█ █", "▀▀▀"],
    "1": [" █ ", " █ ", " ▀ "],
    "2": ["▀▀█", "█▀▀", "▀▀▀"],
    "3": ["▀▀█", " ▀█", "▀▀▀"],
    "4": ["█ █", "▀▀█", "  ▀"],
    "5": ["█▀▀", "▀▀█", "▀▀▀"],
    "6": ["█▀▀", "█▀█", "▀▀▀"],
    "7": ["▀▀█", "  █", "  ▀"],
    "8": ["█▀█", "█▀█", "▀▀▀"],
    "9": ["█▀█", "▀▀█", "▀▀▀"],
}

_SEPARATOR: list[str] = ["   ", "▀▀▀", "   "]
_DIGIT_GAP = " "


def _number_rows(n: int) -> list[str]:
    """Return the 3 rows for a non-negative integer, digits separated by a space."""
    n = max(0, int(n))
    digits = str(n)
    rows = ["", "", ""]
    for i, ch in enumerate(digits):
        glyph = GLYPHS[ch]
        for row in range(3):
            if i > 0:
                rows[row] += _DIGIT_GAP
            rows[row] += glyph[row]
    return rows


def render_score(home: int, away: int, sep_gap: str = "  ") -> str:
    """
    Render *home* and *away* as a 3-line half-block score string.

    The separator glyph is placed between the two numbers with *sep_gap*
    padding on each side.  Multi-digit scores are handled by iterating over
    each digit and joining with a single space between glyphs.

    Returns a ``\\n``-joined string of exactly 3 lines.
    """
    home_rows = _number_rows(home)
    away_rows = _number_rows(away)

    lines: list[str] = []
    for row in range(3):
        line = (
            home_rows[row]
            + sep_gap
            + _SEPARATOR[row]
            + sep_gap
            + away_rows[row]
        )
        lines.append(line)
    return "\n".join(lines)
