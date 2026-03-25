# data_loader.py
# Handles all reading and writing of local data files,
# plus loading and parsing the MovieLens small dataset.

from pathlib import Path
import zipfile
import requests
import pandas as pd

from movie_rating_tool.models import UserRating, RatingCollection, Movie


PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RATINGS_FILE = DATA_DIR / "my_ratings.csv"
MOVIES_CACHE_FILE = DATA_DIR / "movies_cache.csv"

# MovieLens dataset files (included in the repo, only ~1MB)
ML_DIR = DATA_DIR / "ml-latest-small"
ML_MOVIES_FILE = ML_DIR / "movies.csv"
ML_RATINGS_FILE = ML_DIR / "ratings.csv"

# MovieLens download URL (only used if dataset is missing)
ML_DOWNLOAD_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


def ensure_data_dir() -> None:
    """Create the /data directory if it doesn't exist yet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)



# MovieLens dataset

def ensure_movielens_data() -> None:
    """
    Make sure the MovieLens dataset is present.
    If not, download and extract it automatically (it's only ~1MB).
    """
    if ML_MOVIES_FILE.exists() and ML_RATINGS_FILE.exists():
        return 

    ensure_data_dir()
    print("📥 MovieLens dataset not found. Downloading (~1MB) ...")

    response = requests.get(ML_DOWNLOAD_URL, stream=True)
    response.raise_for_status()

    zip_path = DATA_DIR / "ml-latest-small.zip"

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DATA_DIR)

    zip_path.unlink()
    print("✅ MovieLens dataset ready.")


def build_movies_cache() -> None:
    """
    Parse the MovieLens movies.csv and ratings.csv,
    merge them, and save a clean movies_cache.csv.

    Each movie gets:
      - title and year (parsed from MovieLens title string)
      - genres
      - mean community rating (used as the "online rating")
      - number of ratings (used as vote count)

    """
    ensure_movielens_data()
    print(" Building movie cache from MovieLens data ...")

    # Load movies
    movies_df = pd.read_csv(ML_MOVIES_FILE)
    # MovieLens titles look like: "Toy Story (1995)"
    # Extract the year from the title string
    movies_df["year"] = movies_df["title"].str.extract(r"\((\d{4})\)$")
    movies_df["clean_title"] = movies_df["title"].str.replace(
        r"\s*\(\d{4}\)$", "", regex=True
    ).str.strip()

    # Drop movies where we couldn't parse a year
    movies_df.dropna(subset=["year"], inplace=True)
    movies_df["year"] = movies_df["year"].astype(int)

    # Load ratings and compute mean rating per movie
    ratings_df = pd.read_csv(ML_RATINGS_FILE)

    # GroupBy movieId → get mean rating and count of ratings
    agg_df = ratings_df.groupby("movieId").agg(
        online_rating=("rating", "mean"),
        num_votes=("rating", "count"),
    ).reset_index()

    # Scale from MovieLens 0.5–5.0 scale → 0–10 scale (multiply by 2)
    agg_df["online_rating"] = (agg_df["online_rating"] * 2).round(1)

    #  Merge movies + aggregated ratings
    merged_df = pd.merge(movies_df, agg_df, on="movieId", how="inner")

    # Only keep movies with at least 10 ratings
    merged_df = merged_df[merged_df["num_votes"] >= 10]



    final_df = merged_df.rename(columns={
        "movieId": "movie_id",
        "clean_title": "title",
        "genres": "genres",
    })[["movie_id", "title", "year", "genres", "online_rating", "num_votes"]]


    final_df["genres"] = final_df["genres"].replace("(no genres listed)", "")

    # most rated movies first
    final_df.sort_values("num_votes", ascending=False, inplace=True)

    final_df.to_csv(MOVIES_CACHE_FILE, index=False)
    print(f"✅ Movie cache built ({len(final_df):,} movies).")


def get_movies_df() -> pd.DataFrame:
    """
    Return the full movie cache as a Pandas DataFrame.
    Builds the cache first if it doesn't exist yet.
    """
    if not is_cache_available():
        build_movies_cache()

    return pd.read_csv(MOVIES_CACHE_FILE)


def is_cache_available() -> bool:
    """Check if the local movie cache exists and has data."""
    if not MOVIES_CACHE_FILE.exists():
        return False
    df = pd.read_csv(MOVIES_CACHE_FILE)
    return not df.empty

# Searching for movies

def search_movies(query: str, limit: int = 10) -> list[dict]:
    """
    Search the movie cache by title (case-insensitive partial match).

    Args:
        query : search string (e.g. "toy story" or "matrix")
        limit : max number of results to return

    Returns:
        List of dicts with movie info, sorted by num_votes descending.

    """
    df = get_movies_df()

    # Case-insensitive partial match on title
    mask = df["title"].str.contains(query, case=False, na=False)
    results_df = df[mask].copy()

    if results_df.empty:
        return []

    # Sort by most-voted first
    results_df.sort_values("num_votes", ascending=False, inplace=True)

    return results_df.head(limit).to_dict(orient="records")


def get_movie_by_id(movie_id: int) -> dict | None:
    """
    Look up a single movie by its MovieLens movie_id.

    Args:
        movie_id : integer movie ID

    Returns:
        A dict with movie info or None if not found.
    """
    df = get_movies_df()
    results = df[df["movie_id"] == movie_id]

    if results.empty:
        return None

    return results.iloc[0].to_dict()



# User Ratings

def save_ratings(collection: RatingCollection) -> None:
    """Save all user ratings to a CSV file using Pandas."""
    ensure_data_dir()

    records = collection.to_list_of_dicts()

    if not records:
        df = pd.DataFrame(columns=["movie_id", "title", "user_score", "review", "rated_on"])
    else:
        df = pd.DataFrame(records)

    df.to_csv(RATINGS_FILE, index=False)
    print(f"✅ Ratings saved to {RATINGS_FILE.name}")


def load_ratings() -> RatingCollection:
    collection = RatingCollection()

    if not RATINGS_FILE.exists():
        return collection

    df = pd.read_csv(RATINGS_FILE)

    if df.empty:
        return collection

    for _, row in df.iterrows():
        try:
            rating = UserRating.from_dict(row.to_dict())
            collection.add(rating)
        except (ValueError, KeyError) as e:
            print(f"⚠️  Skipping malformed row: {e}")

    return collection




def get_data_summary() -> dict:
    """Return a summary of what's stored locally."""
    summary = {
        "ratings_file_exists": RATINGS_FILE.exists(),
        "cache_file_exists": MOVIES_CACHE_FILE.exists(),
        "num_ratings": 0,
        "num_cached_movies": 0,
    }

    if summary["ratings_file_exists"]:
        df = pd.read_csv(RATINGS_FILE)
        summary["num_ratings"] = len(df)

    if summary["cache_file_exists"]:
        df = pd.read_csv(MOVIES_CACHE_FILE)
        summary["num_cached_movies"] = len(df)

    return summary