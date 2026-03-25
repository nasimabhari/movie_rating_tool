# cli.py
# Entry point for the command-line interface.
# for now this tests our data storage layer.

from movie_rating_tool.models import UserRating, RatingCollection
from movie_rating_tool import data_loader


def run_cli():
    print("🎬 Welcome to Movie Rating Tool!")
    print()

    # Create a sample rating
    rating1 = UserRating(
        imdb_id="tt0111161",
        title="The Shawshank Redemption",
        user_score=9.5,
        review="Timeless masterpiece.",
    )
    rating2 = UserRating(
        imdb_id="tt0068646",
        title="The Godfather",
        user_score=9.0,
        review="Perfect filmmaking.",
    )

    # Add to collection and save
    collection = RatingCollection()
    collection.add(rating1)
    collection.add(rating2)

    print(f"📋 Collection before save: {collection}")
    data_loader.save_ratings(collection)

    # Load back and verify
    print()
    loaded = data_loader.load_ratings()
    print(f"📂 Loaded from CSV: {loaded}")
    for r in loaded.all():
        print(f"   • {r.title} → {r.user_score}/10  (rated on {r.get_date_str()})")

    # Show summary
    print()
    summary = data_loader.get_data_summary()
    print("📊 Data summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")