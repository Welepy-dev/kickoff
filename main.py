from api.endpoints import get_all_matches
from models.fixture import parse_fixtures

def main():
    raw = get_all_matches()
    fixtures = parse_fixtures(raw)

    # Sort by date ascending (soonest first)
    # fixtures.sort(key=lambda f: f.date)

    fixtures.sort(key=lambda f: f.date, reverse=True)

    for f in fixtures:
        print(f"Game: {f.name}, date: {f.date}")

if __name__ == "__main__":
    main()
