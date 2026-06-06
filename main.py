from api.constants import LALIGA_ID, UCL_ID
from api.endpoints import get_all_matches
from models.fixture import parse_fixtures

def main():
    fixtures = parse_fixtures(get_all_matches())
    for fixture in fixtures:
        if fixture.competition_id == UCL_ID and fixture.homeTeam == 'Barça' or fixture.awayTeam == 'Barça' and fixture.competition_id != LALIGA_ID:
            print(fixture.score)

if __name__ == "__main__":
    main()
