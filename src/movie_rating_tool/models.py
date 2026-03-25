# models.py
# Defines the core data models for the Movie Rating Tool.

from dataclasses import dataclass, field
from datetime import date


# Movie class — represents a movie fetched from the IMDb dataset

class Movie:
    """
    Represents a movie from the MovieLens dataset.

    Attributes:
        movie_id     : unique MovieLens integer ID
        title        : movie title
        year         : release year
        genres       : a SET of genre strings (e.g. {"Drama", "Crime"})
        online_rating: mean community rating scaled to 0–10
        num_votes    : number of community ratings
    """

    def __init__(
        self,
        movie_id: int,
        title: str,
        year: int,
        genres: set[str],
        online_rating: float,
        num_votes: int,
    ):
        self.movie_id: int = movie_id
        self.title: str = title
        self.year: int = year
        self.genres: set[str] = genres
        self.online_rating: float = online_rating
        self.num_votes: int = num_votes

    def __repr__(self) -> str:
        return (
            f"Movie(title={self.title!r}, year={self.year}, "
            f"rating={self.online_rating}, genres={self.genres})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return False
        return self.movie_id == other.movie_id

    def to_dict(self) -> dict:
        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "year": self.year,
            "genres": ",".join(sorted(self.genres)),
            "online_rating": self.online_rating,
            "num_votes": self.num_votes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Movie":
        return cls(
            movie_id=int(data["movie_id"]),
            title=data["title"],
            year=int(data["year"]),
            genres=set(data["genres"].split(",")) if data["genres"] else set(),
            online_rating=float(data["online_rating"]),
            num_votes=int(data["num_votes"]),
        )


# UserRating class — represents a single rating given by the user

class UserRating:
    """
    Represents a personal rating given by the user to a movie.

    Attributes:
        movie_id  : links to a Movie (integer MovieLens ID)
        title     : movie title (stored for convenience)
        user_score: the user's rating (float, 0.0–10.0)
        review    : optional short text review
        rated_on  : date the rating was added (tuple: year, month, day)
    """

    def __init__(
        self,
        movie_id: int,
        title: str,
        user_score: float,
        review: str = "",
        rated_on: date | None = None,
    ):
        if not (0.0 <= user_score <= 10.0):
            raise ValueError(f"Score must be between 0 and 10, got {user_score}")

        self.movie_id: int = movie_id
        self.title: str = title
        self.user_score: float = round(user_score, 1)
        self.review: str = review

        _date = rated_on or date.today()
        self.rated_on: tuple[int, int, int] = (_date.year, _date.month, _date.day)

    def __repr__(self) -> str:
        return (
            f"UserRating(title={self.title!r}, "
            f"score={self.user_score}, date={self.rated_on})"
        )

    def get_date_str(self) -> str:
        year, month, day = self.rated_on
        return f"{year}-{month:02d}-{day:02d}"

    def to_dict(self) -> dict:
        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "user_score": self.user_score,
            "review": self.review,
            "rated_on": self.get_date_str(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserRating":
        year, month, day = data["rated_on"].split("-")
        rated_on = date(int(year), int(month), int(day))

        return cls(
            movie_id=int(data["movie_id"]),
            title=data["title"],
            user_score=float(data["user_score"]),
            review=data.get("review", ""),
            rated_on=rated_on,
        )



# RatingCollection class — manages a list of UserRatings


class RatingCollection:
    """
    Manages all of the user's personal ratings.
    Uses a list for storage and a set for fast duplicate checking.
    """

    def __init__(self):
        self._ratings: list[UserRating] = []
        self._rated_ids: set[int] = set()   # set of movie_ids already rated

    def add(self, rating: UserRating) -> bool:
        if rating.movie_id in self._rated_ids:
            return False
        self._ratings.append(rating)
        self._rated_ids.add(rating.movie_id)
        return True

    def remove(self, movie_id: int) -> bool:
        for i, r in enumerate(self._ratings):
            if r.movie_id == movie_id:
                self._ratings.pop(i)
                self._rated_ids.discard(movie_id)
                return True
        return False

    def get(self, movie_id: int) -> UserRating | None:
        for r in self._ratings:
            if r.movie_id == movie_id:
                return r
        return None

    def all(self) -> list[UserRating]:
        return list(self._ratings)

    def count(self) -> int:
        return len(self._ratings)

    def has(self, movie_id: int) -> bool:
        return movie_id in self._rated_ids

    def get_all_genres(self) -> set[str]:
        all_genres: set[str] = set()
        return all_genres

    def to_list_of_dicts(self) -> list[dict]:
        return [r.to_dict() for r in self._ratings]

    def __len__(self) -> int:
        return len(self._ratings)

    def __repr__(self) -> str:
        return f"RatingCollection({len(self._ratings)} ratings)"