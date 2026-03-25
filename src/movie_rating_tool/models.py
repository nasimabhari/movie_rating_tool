# models.py
# Defines the core data models for the Movie Rating Tool.

from dataclasses import dataclass, field
from datetime import date


# Movie class — represents a movie fetched from the IMDb dataset

class Movie:
    """
    Represents a movie with its IMDb metadata.

    Attributes:
        imdb_id   : unique IMDb identifier (e.g. "tt0111161")
        title     : movie title
        year      : release year
        genres    : a SET of genre strings (e.g. {"Drama", "Crime"})
        imdb_rating: average IMDb rating (float, 0.0–10.0)
        num_votes : number of IMDb votes
    """

    def __init__(
        self,
        imdb_id: str,
        title: str,
        year: int,
        genres: set[str],
        imdb_rating: float,
        num_votes: int,
    ):
        # Basic attributes (variables & types)
        self.imdb_id: str = imdb_id
        self.title: str = title
        self.year: int = year
        self.genres: set[str] = genres
        self.imdb_rating: float = imdb_rating
        self.num_votes: int = num_votes

    def __repr__(self) -> str:
        return (
            f"Movie(title={self.title!r}, year={self.year}, "
            f"imdb={self.imdb_rating}, genres={self.genres})"
        )

    def __eq__(self, other: object) -> bool:
        """Two movies are equal if they share the same IMDb ID."""
        if not isinstance(other, Movie):
            return False
        return self.imdb_id == other.imdb_id

    def to_dict(self) -> dict:
        """
        Convert the Movie to a plain dictionary.
        Useful for saving to CSV / JSON later.
        """
        return {
            "imdb_id": self.imdb_id,
            "title": self.title,
            "year": self.year,
            "genres": ",".join(sorted(self.genres)),
            "imdb_rating": self.imdb_rating,
            "num_votes": self.num_votes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Movie":
        """
        Create a Movie from a plain dictionary.
        Used when loading data back from CSV / JSON.
        """
        return cls(
            imdb_id=data["imdb_id"],
            title=data["title"],
            year=int(data["year"]),
            genres=set(data["genres"].split(",")) if data["genres"] else set(),
            imdb_rating=float(data["imdb_rating"]),
            num_votes=int(data["num_votes"]),
        )


# UserRating class — represents a single rating given by the user

class UserRating:
    """
    Represents a personal rating that the user gives to a movie.

    Attributes:
        imdb_id   : links to a Movie
        title     : movie title (stored for convenience)
        user_score: the user's rating (float, 0.0–10.0)
        review    : optional short text review
        rated_on  : date the rating was added (tuple: year, month, day)
    """

    def __init__(
        self,
        imdb_id: str,
        title: str,
        user_score: float,
        review: str = "",
        rated_on: date | None = None,
    ):
        if not (0.0 <= user_score <= 10.0):
            raise ValueError(f"Score must be between 0 and 10, got {user_score}")

        self.imdb_id: str = imdb_id
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
            "imdb_id": self.imdb_id,
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
            imdb_id=data["imdb_id"],
            title=data["title"],
            user_score=float(data["user_score"]),
            review=data.get("review", ""),
            rated_on=rated_on,
        )



# RatingCollection class — manages a list of UserRatings


class RatingCollection:
    """
    Manages all of the user's personal ratings.

    Internally stores ratings in a list and tracks rated IMDb IDs
    in a set for O(1) duplicate checking.

    """

    def __init__(self):
        self._ratings: list[UserRating] = []

        self._rated_ids: set[str] = set()

    def add(self, rating: UserRating) -> bool:
        """
        Add a new UserRating to the collection.
        Returns True if added, False if this movie was already rated.
        """
        if rating.imdb_id in self._rated_ids:
            return False 

        self._ratings.append(rating)
        self._rated_ids.add(rating.imdb_id)
        return True

    def remove(self, imdb_id: str) -> bool:
        """
        Remove a rating by IMDb ID.
        Returns True if removed, False if not found.
        """
        for i, r in enumerate(self._ratings):
            if r.imdb_id == imdb_id:
                self._ratings.pop(i)
                self._rated_ids.discard(imdb_id)
                return True
        return False

    def get(self, imdb_id: str) -> UserRating | None:
        """Fetch a single rating by IMDb ID. Returns None if not found."""
        for r in self._ratings:
            if r.imdb_id == imdb_id:
                return r
        return None

    def all(self) -> list[UserRating]:
        return list(self._ratings)

    def count(self) -> int:
        return len(self._ratings)

    def has(self, imdb_id: str) -> bool:
        return imdb_id in self._rated_ids

    def get_all_genres(self) -> set[str]:
        """
        Return a set of all unique genres the user has rated.
        Demonstrates: set union across multiple sets.
        """
        all_genres: set[str] = set()
        for r in self._ratings:
            # We'll enrich this from Movie data later. for now check review
            pass
        return all_genres

    def to_list_of_dicts(self) -> list[dict]:
        return [r.to_dict() for r in self._ratings]

    def __len__(self) -> int:
        return len(self._ratings)

    def __repr__(self) -> str:
        return f"RatingCollection({len(self._ratings)} ratings)"