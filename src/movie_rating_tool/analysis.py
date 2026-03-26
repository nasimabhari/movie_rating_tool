# analysis.py
# Statistical analysis of the user's movie ratings.

import numpy as np
import pandas as pd

from movie_rating_tool.models import RatingCollection
from movie_rating_tool import data_loader, rating_engine



def compute_stats(collection: RatingCollection) -> dict:
    """
    Compute a full set of statistics about the user's ratings.

    Uses NumPy for numerical calculations and Pandas for
    grouped analysis.

    Args:
        collection : the user's RatingCollection

    Returns:
        A dictionary of statistics. Keys include:
            count, mean, median, std, min_score, max_score,
            min_title, max_title, mean_online, mean_diff,
            genre_counts, score_distribution

    """

  
    scores: list[float] = [r.user_score for r in collection.all()]

    scores_array = np.array(scores)

    # Basic NumPy statistics
    mean_score   = round(float(np.mean(scores_array)), 2)
    median_score = round(float(np.median(scores_array)), 2)
    std_score    = round(float(np.std(scores_array)), 2)
    min_score    = round(float(np.min(scores_array)), 1)
    max_score    = round(float(np.max(scores_array)), 1)

    # Find the titles for best and worst rated movies
    min_title = ""
    max_title = ""

    for rating in collection.all():
        if rating.user_score == min_score:
            min_title = rating.title
        if rating.user_score == max_score:
            max_title = rating.title

    # user score vs online rating
    comparison_df = rating_engine.get_comparison_df(collection)

    mean_online = 0.0
    mean_diff   = 0.0

    if not comparison_df.empty:
        valid_df = comparison_df.dropna(subset=["online_rating", "difference"])

        if not valid_df.empty:
            mean_online = round(float(np.mean(valid_df["online_rating"].values)), 2)
            mean_diff   = round(float(np.mean(valid_df["difference"].values)), 2)



    genre_counts = _compute_genre_counts(collection)

    # Bin scores into ranges: 0-2, 2-4, 4-6, 6-8, 8-10
    counts, bin_edges = np.histogram(scores_array, bins=[0, 2, 4, 6, 8, 10])

    score_distribution: dict[str, int] = {}
    for i in range(len(counts)):
        label = f"{int(bin_edges[i])}–{int(bin_edges[i+1])}"
        score_distribution[label] = int(counts[i])

    return {
        "count":              collection.count(),
        "mean":               mean_score,
        "median":             median_score,
        "std":                std_score,
        "min_score":          min_score,
        "max_score":          max_score,
        "min_title":          min_title,
        "max_title":          max_title,
        "mean_online":        mean_online,
        "mean_diff":          mean_diff,
        "genre_counts":       genre_counts,
        "score_distribution": score_distribution,
        "scores_array":       scores_array,
    }



# Genre analysis
def _compute_genre_counts(collection: RatingCollection) -> dict[str, int]:
    """
    Count how many movies the user has rated per genre.

    Returns a dict sorted by count descending, e.g.:
        {"Drama": 5, "Action": 3, "Comedy": 2}
    """

    genre_counts: dict[str, int] = {}

    for rating in collection.all():
        movie = data_loader.get_movie_by_id(rating.movie_id)

        if not movie or not movie["genres"]:
            continue

        # MovieLens stores genres as "Action|Adventure|Sci-Fi"
        genres = movie["genres"].split("|")

        for genre in genres:
            genre = genre.strip()
            if not genre or genre == "(no genres listed)":
                continue
            genre_counts[genre] = genre_counts.get(genre, 0) + 1


    sorted_genres = dict(
        sorted(genre_counts.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_genres


def get_genre_stats(collection: RatingCollection) -> pd.DataFrame:
    """
    Build a Pandas DataFrame with average user score per genre.
    Returns a DataFrame with columns:
        genre, avg_user_score, avg_online_rating, count

    """
    if collection.count() == 0:
        return pd.DataFrame()

    rows: list[dict] = []

    for rating in collection.all():
        movie = data_loader.get_movie_by_id(rating.movie_id)

        if not movie or not movie["genres"]:
            continue

        genres = movie["genres"].split("|")

        for genre in genres:
            genre = genre.strip()
            if not genre or genre == "(no genres listed)":
                continue

            rows.append({
                "genre":         genre,
                "user_score":    rating.user_score,
                "online_rating": movie["online_rating"],
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    genre_df = df.groupby("genre").agg(
        avg_user_score   = ("user_score",    "mean"),
        avg_online_rating= ("online_rating", "mean"),
        count            = ("user_score",    "count"),
    ).reset_index()


    genre_df["avg_user_score"]    = genre_df["avg_user_score"].round(2)
    genre_df["avg_online_rating"] = genre_df["avg_online_rating"].round(2)

    genre_df.sort_values("count", ascending=False, inplace=True)

    return genre_df


def get_percentile_rank(score: float, collection: RatingCollection) -> float:
    """
    Return what percentile a given score is in, within the user's ratings.

    For example: 85.0 means this score is higher than 85% of your ratings.

    Args:
        score      : the score to rank
        collection : the user's full collection

    Returns:
        Percentile as a float (0.0 – 100.0)
    """
    scores = np.array([r.user_score for r in collection.all()])

    rank = float(np.sum(scores < score) / len(scores) * 100)

    return round(rank, 1)