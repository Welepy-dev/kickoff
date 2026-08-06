# kickoff — Bug & Problem Report

Static review of the whole codebase (API layer, models, Textual UI, bigscore
font, tests). Files were compiled with `python -m py_compile` (all pass) but
runtime deps (`textual`, `requests-cache`, etc.) are not installed in this
environment, so no live UI run was possible.

Severity legend: **CRITICAL** (crash / data loss) · **HIGH** (broken feature /
will break in practice) · **MEDIUM** (edge-case crash / wrong behaviour) ·
**LOW** (cleanup / minor).

---

## CRITICAL

### C1. `parse_fixtures` crashes on postponed / cancelled / abandoned matches
`models/fixture.py:27-37`

```python
home_score = match['score']['fullTime']['home']
...
home_short = match['homeTeam']['shortName'] or ...
away_short = match['awayTeam']['shortName'] or ...
```

football-data.org sets `score` to `null` for `POSTPONED` / `CANCELLED` /
`ABANDONED` matches, and `homeTeam` / `awayTeam` to `null` for cup matches
where the opponent isn't decided yet. Both cases raise `TypeError` /
`KeyError` *before* the `status` check on line 53, which kills the whole
`load_fixtures` worker and leaves the UI stuck on the loading spinner.

Fix: guard with `.get(...)` / `isinstance` checks before indexing, and fall
back to `0`/`"-"`/`"TBD"`.

### C2. No error handling anywhere in the fetch path → UI silently dead on any API failure
`ui/app.py:65-122`, `ui/leagueScreen.py:105-190`, `api/endpoints.py:17-33`

Every network call is unguarded: `get()` does `raise_for_status()` and the
`@work(thread=True)` methods never wrap anything in `try/except`. If the API
is down, rate-limited (429) or a token is missing, the worker thread dies,
nothing is rendered, the `#loading` indicator is never removed, and the user
gets no message. `_populate_tables` even swallows the removal exception
silently.

Fix: catch exceptions in the workers, `call_from_thread` an error message /
retry UI.

### C3. First launch fires ~20 concurrent requests and trips the API rate limit
`api/endpoints.py:19-24`, `api/client.py:34-41`

`load_fixtures` → `get_all_matches()` and `load_scorers` →
`get_all_top_scorers()` each spin up `ThreadPoolExecutor(max_workers=10)` and
run **simultaneously** (two `@work(thread=True)` methods started back-to-back
in `on_mount`). That's ~20 parallel requests against the football-data.org
free tier (~10 req/min). The first run will reliably return a pile of 429s,
which then trigger C2. `requests-cache` only saves you *after* a successful
run.

Fix: serialize/limit concurrency (small pool, delay, or one worker that does
both fetches sequentially) and retry on 429.

### C4. `get_all_*` aborts the entire batch on a single competition failure
`api/endpoints.py:17-24`

`future.result()` in the `as_completed` loop re-raises the first exception and
discards the (valid) results already fetched. `COMPETITION_IDS` includes
`WORLDCUP_ID` (2000) and `EURO_ID` (2018) (`utils.py:12-15`); off-season
these endpoints can return 404/empty, and one such failure bricks the whole
main screen instead of degrading gracefully.

Fix: catch per-future exceptions and keep `None`/partial results.

---

## HIGH

### H1. `Standing` model never parses `form` → "Last 5" column is always empty
`models/standing.py:3-16`, `ui/leagueScreen.py:114`

`load_standings` does `getattr(s, "form", None) or []`, but the `Standing`
dataclass has **no `form` field** and `parse_standings` never reads
`row["form"]`. The API provides it (e.g. `"WWDLW"`), so the whole column is
silently blank.

Secondary bug in the same code: even if `form` were populated, the API returns
a 5-char string like `"WWDLW"`, but `ui/styles.py:103-119` (`style_form`)
splits on spaces and expects tokens `"W"`, `"L"`, `"D"`; a 5-char string would
render as one dimmed token. The rendering logic is designed for a space-joined
string ("W W D L W") that the parse never produces.

Fix: add `form: str` to `Standing`, parse `row["form"]`, and make `style_form`
iterate characters (or join with spaces before calling).

### H2. No validation of env config → cryptic failures
`api/client.py:18-32`

`API_KEY` / `BASE_URL` are raw `os.getenv()` calls. If `.env` is missing:
- `_session.headers.update({"X-Auth-Token": None})` sends the literal string
  `"None"`.
- `f"{None}/competitions"` → `requests` raises `InvalidURL: No host supplied`.

There is no `.env.example` and the README doesn't document the required vars.
Fix: fail fast at startup with a clear message.

### H3. `get_competition_id` falls back to a magic `1` for unknown leagues
`utils.py:17-38`

Unknown/typo'd league names return `1`, which is not a valid
football-data.org competition ID → 404 → C2 dead UI. Also, the league list is
duplicated between `ui/leaguePopup.py:9-20` and `utils.py`; adding a league to
one without the other silently produces wrong IDs. Fix: raise / return
`None`, and drive the popup from `utils.COMPETITION_IDS`.

### H4. `requests_cache.install_cache` + `CachedSession` open the same SQLite file twice
`api/client.py:7-31`

The module-level `install_cache` (lines 7-16) is dead code — every request
goes through the separately created `CachedSession`. Two SQLite handles on
the same DB file can produce intermittent `database is locked`, and the
global patch is pointless. Remove the `install_cache` block.

---

## MEDIUM

### M1. Negative / non-integer scores crash `render_score`
`bigscore.py:29-39`

`str(n)` of a negative number yields `"-1"` and `GLYPHS[ch]` raises
`KeyError: '-'` (verified). `BigScore` (`widgets.py:21-23`) calls
`render_score(self.home, self.away)` with no guard; a `None`/negative value
from upstream data would crash the render. Fix: clamp/clip to `max(0, n)` and
coerce non-ints.

### M2. Timezone bug — UTC shown as local; naive/aware comparison fragile
`ui/fixture_list.py:58-59`, `ui/app.py:116`, `ui/leagueScreen.py:148`

`datetime.fromisoformat(dt.replace("Z", "+00:00"))` is timezone-aware, so the
`dt < now` comparison happens to be correct, but the displayed kickoff time
(`dt.day`, `dt.hour`…) is shown in UTC, not the user's local time. Also the
`replace("Z", "+00:00")` trick silently breaks if the API ever sends an
offset other than `Z`. Fix: convert to local time with `astimezone()` and use
`datetime.fromisoformat` on the raw string (py ≥3.11 parses `Z`).

### M3. Postponed matches with past dates land in "Previous" as if played
`ui/app.py:117`, `ui/leagueScreen.py:149`

Classification is `if f.fulltime or dt < now: previous`. A postponed fixture
whose kickoff has already passed is shown in the "Previous" tab but rendered
as an unplayed `VS` card (never scored). Fix: only time-based classification
for non-finished matches, or show a `POSTPONED` marker.

### M4. `previous_fixtures.insert(0, ...)` is O(n²)
`ui/app.py:118`, `ui/leagueScreen.py:150`

For several thousand matches (all comps), repeated `list.insert(0)` is
quadratic. `previous_fixtures.reverse()` after the loop (or build in
descending order) is O(n).

### M5. `#cards-container` centered content clips when overflowing
`ui/styles/fixture_list.css:20-29`

`align: center middle` + `overflow-y: auto` centers children that exceed the
container height, clipping the top/bottom with no way to scroll to them — a
known Textual gotcha. With 5 cards per page (`PAGE_SIZE=5`,
`ui/fixture_list.py:13`) this can cut off content on short terminals. Fix:
`align: center top` or remove `align` and use margins.

### M6. Scorers `KeyError` risk on optional fields
`models/scorer.py:27-37`

`player["player"]["nationality"]` and `player["assists"]` /
`player["penalties"]` are indexed unconditionally but are not always present
in the API response for every competition. One missing key raises and kills
the whole scorers load. Use `.get(...)` with defaults.

### M7. `competition_id` annotated `str` but assigned an `int`
`models/fixture.py:8`

```python
competition_id: str   # but assigned match["competition"]["id"] (an int)
```
Type-annotation mismatch; harmless at runtime but confusing and will fail
`mypy`/`pyright` checks.

### M8. Duplicate / stale cache file location
`api/client.py:7-31`

`"football_cache"` is a relative path — the SQLite cache is created in the
process's CWD. Running the app from different directories creates multiple
caches and re-triggers C3. Fix: an absolute path (e.g. `~/.cache/kickoff/`).

---

## LOW

- **L1. Dead code**: `ui/FixtureWidget.py` (superseded by `ui/fixture_card.py`),
  `get_match()` (`api/endpoints.py:35-36`), unused style helpers `style_date`,
  `style_team`, `style_score`, `style_competition`, `style_time`
  (`ui/styles.py:27-66`).
- **L2. Unused dependency**: `pyfiglet` in `pyproject.toml:8` — replaced by
  `bigscore.py`.
- **L3. `textual-dev` is a dev tool but listed as a runtime dependency**:
  `pyproject.toml:13`.
- **L4. No `__init__.py` in `api/`, `models/`, `ui/`, `tests/`**: works as
  namespace packages only when launched from the repo root; `pip install .`
  won't package anything, and imports break if run from another directory.
- **L5. `previous_fixtures` uses `insert(0, ...)` while the equivalent in
  `leagueScreen` duplicates the same logic** — the split-into-next/previous
  code is copy-pasted between `ui/app.py:112-120` and
  `ui/leagueScreen.py:144-152`.
- **L6. Two BigScore refreshes** when both scores change (`demo_app.py:61-65`,
  `widgets.py:25-29`): `watch_home` and `watch_away` each call `refresh()`.
- **L7. `ui/fixture_card.py:35-40`**: winner color logic is fine, but the CSS
  for `.card-away` is commented out (`ui/styles/fixture_card.css:47-51`), so
  the away team label uses default alignment (left/top) while `.card-home` is
  right/bottom — visually inconsistent.
- **L8. Empty-state pagination label** shows `Page 0/0`
  (`ui/fixture_list.py:53`) while `total_pages` returns `max(1, ...)` = 1
  (line 22) — inconsistent.
- **L9. CSS specificity smell**: `app.css:11-14` `Vertical { border…; width:
  1fr; }` applies globally to every `Vertical` in every screen (including
  inside `FixtureCard` and the popup), requiring per-widget overrides.
  Scoping to `#main > Vertical` would be safer.
- **L10. `pyproject.toml:5`** description still says *"Add your description
  here"*.
- **L11. `matches` shown for all 10 competitions, including off-season World
  Cup/Euro**; combined with the `matchday` grouping this floods the "Next"
  tab with irrelevant fixtures. Consider an active-competition filter.
- **L12. `datetime.fromisoformat` is called in three places with the same
  `"Z"`-replace idiom** — extract a small `parse_utc()` helper.
- **L13. `.gitignore` ignores all `*.txt`** (`api/...` docs, notes, etc. would
  be silently untracked).

---

## Summary of the most impactful fixes

1. Harden `parse_fixtures` against `None` score/team (`C1`).
2. Add try/except + user-visible error handling to the workers (`C2`).
3. Serialize/limit the API fan-out and retry on 429 (`C3`, `C4`).
4. Add `form` to `Standing` and fix `style_form` so "Last 5" actually shows
   (`H1`).
5. Validate env vars at startup and drop the redundant `install_cache` (`H2`,
   `H4`).
