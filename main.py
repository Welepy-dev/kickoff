from api.endpoints import get_all_matches, get_all_top_scorers
from models.fixture import parse_fixtures
from models.scorer import parse_scorers
from ui.app import UI

def main():
    matches = parse_fixtures(get_all_matches())
    scorers = parse_scorers(get_all_top_scorers())

    ui = UI()
    ui.run()

if __name__ == "__main__":
    main()
