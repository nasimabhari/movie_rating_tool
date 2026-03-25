# data_loader.py
# Handles all reading and writing of local data files.

from pathlib import Path
import pandas as pd

from movie_rating_tool.models import UserRating, RatingCollection, Movie


# Path constants — all data lives in the /data folder

# Walk up from this file → src/movie_rating_tool → src → project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# File paths
RATINGS_FILE = DATA_DIR / "my_ratings.csv"
MOVIES_CACHE_FILE = DATA_DIR / "movies_cache.csv"


def ensure_data_dir() -> None:
    """Create the /data directory if it doesn't exist yet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# User Ratings — save & load

def save_ratings(collection: RatingCollection) -> None:
    """
    Save all user ratings to a CSV file using Pandas.

    Args:
        collection: the RatingCollection to persist
    """
    ensure_data_dir()

    records = collection.to_list_of_dicts()

    if not records:
        # If there are no ratings, write an empty CSV with just the headers
        df = pd.DataFrame(columns=["imdb_id", "title", "user_score", "review", "rated_on"])
    else:
        df = pd.DataFrame(records)

    df.to_csv(RATINGS_FILE, index=False)
    print(f"✅ Ratings saved to {RATINGS_FILE}")


def load_ratings() -> RatingCollection:
    """
    Load user ratings from CSV into a RatingCollection.

    Returns an empty RatingCollection if the file doesn't exist yet.
    """
    collection = RatingCollection()

    if not RATINGS_FILE.exists():
        return collection

    df = pd.read_csv(RATINGS_FILE)

    if df.empty:
        return collection

    # Loop through each row and reconstruct UserRating objects
    for _, row in df.iterrows():
        try:
            rating = UserRating.from_dict(row.to_dict())
            collection.add(rating)
        except (ValueError, KeyError) as e:
            print(f"⚠️  Skipping malformed row: {e}")

    return collection


# Movie Metadata Cache — save & load


def save_movies_cache(movies: list[Movie]) -> None:
    """
    Save a list of Movie objects to a local CSV cache.

    Args:
        movies: list of Movie objects to cache
    """
    ensure_data_dir()

    records = [m.to_dict() for m in movies]
    df = pd.DataFrame(records)
    df.to_csv(MOVIES_CACHE_FILE, index=False)
    print(f"✅ Movie cache saved ({len(movies)} movies)")


def load_movies_cache() -> list[Movie]:
    """
    Load the movie metadata cache from CSV.

    Returns an empty list if the cache doesn't exist yet.
    """
    if not MOVIES_CACHE_FILE.exists():
        return []

    df = pd.read_csv(MOVIES_CACHE_FILE)

    if df.empty:
        return []

    movies = []
    for _, row in df.iterrows():
        try:
            movie = Movie.from_dict(row.to_dict())
            movies.append(movie)
        except (ValueError, KeyError) as e:
            print(f"⚠️  Skipping malformed movie row: {e}")

    return movies


def is_cache_available() -> bool:
    """Check if the local movie cache file exists and is not empty."""
    if not MOVIES_CACHE_FILE.exists():
        return False

    # Also check the file actually has data rows
    df = pd.read_csv(MOVIES_CACHE_FILE)
    return not df.empty


# Utility — quick summary of saved data


def get_data_summary() -> dict:
    """
    Return a summary dictionary of what's stored locally.
    Useful for displaying stats in the CLI.
    """
    summary = {
        "ratings_file_exists": RATINGS_FILE.exists(),
        "cache_file_exists": MOVIES_CACHE_FILE.exists(),
        "num_ratings": 0,
        "num_cached_movies": 0,
    }

    # Count saved ratings
    if summary["ratings_file_exists"]:
        df = pd.read_csv(RATINGS_FILE)
        summary["num_ratings"] = len(df)

    # Count cached movies
    if summary["cache_file_exists"]:
        df = pd.read_csv(MOVIES_CACHE_FILE)
        summary["num_cached_movies"] = len(df)

    return summary