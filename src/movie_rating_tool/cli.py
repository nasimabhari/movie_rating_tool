# cli.py
# search the MovieLens dataset.

from movie_rating_tool import data_loader


def run_cli():
    print("🎬 Welcome to Movie Rating Tool!")
    print()

    print("🔍 Searching for 'toy story' ...")
    results = data_loader.search_movies("toy story", limit=5)

    if not results:
        print("No results found.")
        return

    print(f"\nTop {len(results)} results:\n")
    for movie in results:
        title = movie["title"]
        year = movie["year"]
        rating = movie["online_rating"]
        votes = movie["num_votes"]
        genres = movie["genres"]
        print(f"  🎬 {title} ({year})")
        print(f"     ⭐ Rating: {rating}/10  |  Votes: {votes:,}  |  Genres: {genres}")
        print()