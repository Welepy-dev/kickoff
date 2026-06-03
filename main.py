from api.constants import BUNDESLIGA_ID
from api.endpoints import get_all_matches, get_matches

def main():
    print(get_all_matches())

if __name__ == "__main__":
    main()
