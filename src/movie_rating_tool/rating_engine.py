# rating_engine.py
# Handles the logic of comparing user ratings with online ratings.


import pandas as pd

from movie_rating_tool import data_loader
from movie_rating_tool.models import RatingCollection, UserRating


def get_comparison_df(collection: RatingCollection) -> pd.DataFrame:
    """
    Build a Pandas DataFrame that joins the user's ratings
    with the online (MovieLens community) ratings.

    Each row contains:
        - title
        - user_score      (the user's personal rating)
        - online_rating   (MovieLens community mean, scaled 0–10)
        - difference      (user_score minus online_rating)
        - year
        - genres

    Args:
        collection : the user's RatingCollection

    Returns:
        A merged DataFrame, or an empty DataFrame if no ratings exist.

    """
    if collection.count() == 0:
        return pd.DataFrame()


    user_df = pd.DataFrame(collection.to_list_of_dicts())


    movies_df = data_loader.get_movies_df()

    merged = pd.merge(
        user_df,
        movies_df[["movie_id", "online_rating", "year", "genres"]],
        on="movie_id",
        how="left",
    )

    merged["difference"] = (merged["user_score"] - merged["online_rating"]).round(1)

    result = merged[[
        "movie_id", "title", "user_score", "online_rating",
        "difference", "year", "genres", "review", "rated_on"
    ]]

    return result


def get_rating_label(score: float) -> str:
    """
    Convert a numeric score (0–10) to a descriptive label.

    Args:
        score : numeric rating

    Returns:
        A string label like "Excellent", "Good", etc.
    """
    if score >= 9.0:
        return "Masterpiece 🏆"
    elif score >= 8.0:
        return "Excellent ⭐"
    elif score >= 7.0:
        return "Good 👍"
    elif score >= 6.0:
        return "Decent 🙂"
    elif score >= 5.0:
        return "Average 😐"
    elif score >= 3.0:
        return "Poor 👎"
    else:
        return "Terrible 💀"


def get_recommendations(collection: RatingCollection, limit: int = 5) -> list[dict]:
    """
    Recommend movies the user hasn't rated yet, based on genres
    they have rated highly (score >= 7.0).

    Strategy:
        1. Find genres the user loves (from highly-rated movies)
        2. Search the movie cache for unrated movies in those genres
        3. Sort by online_rating and return the top results

    Args:
        collection : the user's RatingCollection
        limit      : how many recommendations to return

    Returns:
        A list of movie dicts recommended for the user.
    """
    if collection.count() == 0:
        return []

    # Step 1, Find genres from highly-rated movies
    liked_genres: set[str] = set()

    for rating in collection.all():
        if rating.user_score >= 7.0:
            # Look up this movie in the cache to get its genres
            movie = data_loader.get_movie_by_id(rating.movie_id)
            if movie and movie["genres"]:
                # Genres are stored as "Action|Adventure|Sci-Fi"
                for genre in movie["genres"].split("|"):
                    liked_genres.add(genre.strip())

    # If the user hasn't liked anything yet, recommend top-rated overall
    if not liked_genres:
        movies_df = data_loader.get_movies_df()
        top = movies_df.sort_values("online_rating", ascending=False).head(limit)
        return top.to_dict(orient="records")

    # Step 2, Find unrated movies in those genres
    movies_df = data_loader.get_movies_df()

    rated_ids: set[int] = {r.movie_id for r in collection.all()}
    unrated_df = movies_df[~movies_df["movie_id"].isin(rated_ids)].copy()


    def matches_genre(genres_str: str) -> bool:
        if not isinstance(genres_str, str):
            return False
        movie_genres = set(genres_str.split("|"))
        # do any genres overlap?
        return len(liked_genres & movie_genres) > 0

    unrated_df = unrated_df[unrated_df["genres"].apply(matches_genre)]

    # Step 3, sort by online rating and return top results
    unrated_df.sort_values("online_rating", ascending=False, inplace=True)

    return unrated_df.head(limit).to_dict(orient="records")