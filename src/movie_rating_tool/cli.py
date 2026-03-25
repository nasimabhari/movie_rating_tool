# cli.py
# The full command-line interface for the Movie Rating Tool.

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt, Confirm
from rich import box

from movie_rating_tool import data_loader
from movie_rating_tool.models import UserRating, RatingCollection
from movie_rating_tool import rating_engine

# Rich console — used for all terminal output (colours, tables, panels)
console = Console()

def run_cli() -> None:
    """
    Main entry point for the CLI.

    Usage:
        uv run -m movie_rating_tool

    Commands:
        add       — add a personal movie rating
        list      — list all your ratings
        compare   — compare your ratings with online ratings
        stats     — show statistics
        plot      — show visualizations
        recommend — get movie recommendations
        search    — search for a movie
        help      — show this help message
    """
    command = sys.argv[1] if len(sys.argv) > 1 else "menu"

    commands: dict[str, callable] = {
        "add":       cmd_add,
        "list":      cmd_list,
        "compare":   cmd_compare,
        "stats":     cmd_stats,
        "plot":      cmd_plot,
        "recommend": cmd_recommend,
        "search":    cmd_search,
        "help":      cmd_help,
        "menu":      cmd_menu,
    }

    print_banner()
    if command in commands:
        commands[command]()
    else:
        console.print(f"[red]Unknown command:[/red] '{command}'")
        console.print("Run [bold]uv run -m movie_rating_tool help[/bold] for usage.")

def print_banner() -> None:
    console.print(Panel.fit(
        "[bold yellow]🎬 Movie Rating Tool[/bold yellow]\n"
        "[dim]Rate movies · Compare with online ratings · Get recommendations[/dim]",
        border_style="yellow",
    ))
    console.print()


def cmd_menu() -> None:
    console.print("[bold]Available commands:[/bold]\n")

    menu_items: list[tuple[str, str]] = [
        ("add",       "Add a personal movie rating"),
        ("list",      "List all your ratings"),
        ("compare",   "Compare your ratings with online ratings"),
        ("stats",     "Show statistics about your ratings"),
        ("plot",      "Show visualizations"),
        ("recommend", "Get movie recommendations"),
        ("search",    "Search for a movie in the database"),
        ("help",      "Show detailed help"),
    ]

    for cmd, description in menu_items:
        console.print(f"  [bold cyan]uv run -m movie_rating_tool {cmd:<10}[/bold cyan] {description}")

    console.print()
    console.print("[dim]Example: uv run -m movie_rating_tool add[/dim]")


def cmd_help() -> None:
    console.print("[bold]Movie Rating Tool — Help[/bold]\n")
    console.print("This tool lets you rate movies and compare with community ratings.\n")
    console.print("[bold]Commands:[/bold]")
    console.print("  [cyan]add[/cyan]       Search for a movie and add your personal rating")
    console.print("  [cyan]list[/cyan]      Display all movies you have rated")
    console.print("  [cyan]compare[/cyan]   Side-by-side: your score vs online rating")
    console.print("  [cyan]stats[/cyan]     Mean, median, and other statistics")
    console.print("  [cyan]plot[/cyan]      Bar chart and distribution visualizations")
    console.print("  [cyan]recommend[/cyan] Suggest movies based on your taste")
    console.print("  [cyan]search[/cyan]    Search the database without rating")
    console.print()
    console.print("[bold]Data source:[/bold] MovieLens small dataset (9,742 movies)")



def cmd_search() -> None:
    query = Prompt.ask("🔍 Search for a movie")

    if not query.strip():
        console.print("[red]Please enter a search term.[/red]")
        return

    results = data_loader.search_movies(query, limit=10)

    if not results:
        console.print(f"[red]No movies found for '{query}'.[/red]")
        return

    table = Table(
        title=f"Search results for '{query}'",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("#",            style="dim",    width=3)
    table.add_column("Title",        style="bold",   min_width=25)
    table.add_column("Year",         justify="center")
    table.add_column("Online Rating",justify="center")
    table.add_column("Votes",        justify="right")
    table.add_column("Genres",       style="dim")

    for i, movie in enumerate(results, start=1):
        table.add_row(
            str(i),
            movie["title"],
            str(movie["year"]),
            f"⭐ {movie['online_rating']}/10",
            f"{int(movie['num_votes']):,}",
            movie["genres"].replace("|", ", "),
        )

    console.print(table)


def cmd_add() -> None:
    """
    Interactively search for a movie and add a personal rating.

    Flow:
        1. User types a search query
        2. Results are shown in a numbered list
        3. User picks a number
        4. User enters score (0–10) and optional review
        5. Rating is saved to CSV
    """
    collection = data_loader.load_ratings()

    query = Prompt.ask("🔍 Search for a movie to rate")

    if not query.strip():
        console.print("[red]Search term cannot be empty.[/red]")
        return

    results = data_loader.search_movies(query, limit=10)

    if not results:
        console.print(f"[red]No movies found for '{query}'. Try a different search.[/red]")
        return

    console.print()
    for i, movie in enumerate(results, start=1):
        console.print(
            f"  [bold cyan]{i:>2}.[/bold cyan] "
            f"[bold]{movie['title']}[/bold] ({movie['year']}) "
            f"— ⭐ {movie['online_rating']}/10 "
            f"[dim]{movie['genres'].replace('|', ', ')}[/dim]"
        )
    console.print()

    choice_str = Prompt.ask(
        f"Enter a number [1–{len(results)}] (or 0 to cancel)"
    )

    if not choice_str.isdigit():
        console.print("[red]Please enter a valid number.[/red]")
        return

    choice = int(choice_str)

    if choice == 0:
        console.print("[dim]Cancelled.[/dim]")
        return

    if not (1 <= choice <= len(results)):
        console.print(f"[red]Please enter a number between 1 and {len(results)}.[/red]")
        return

    selected = results[choice - 1]
    movie_id = int(selected["movie_id"])

    if collection.has(movie_id):
        existing = collection.get(movie_id)
        console.print(
            f"[yellow]You already rated [bold]{selected['title']}[/bold] "
            f"with {existing.user_score}/10.[/yellow]"
        )
        overwrite = Confirm.ask("Do you want to overwrite it?")
        if not overwrite:
            return
        # Remove the old rating so we can add the new one
        collection.remove(movie_id)

    console.print(
        f"\n🎬 Rating: [bold]{selected['title']}[/bold] ({selected['year']})"
    )
    console.print(f"   Online rating: ⭐ {selected['online_rating']}/10\n")

    while True:
        score_str = Prompt.ask("Your score (0.0 – 10.0)")
        try:
            score = float(score_str)
            if 0.0 <= score <= 10.0:
                break
            else:
                console.print("[red]Score must be between 0.0 and 10.0.[/red]")
        except ValueError:
            console.print("[red]Please enter a number like 8.5[/red]")

    review = Prompt.ask("Short review (optional, press Enter to skip)", default="")

    new_rating = UserRating(
        movie_id=movie_id,
        title=selected["title"],
        user_score=score,
        review=review,
    )

    collection.add(new_rating)
    data_loader.save_ratings(collection)

    label = rating_engine.get_rating_label(score)
    console.print(
        f"\n✅ Saved! [bold]{selected['title']}[/bold] → "
        f"[bold green]{score}/10[/bold green] — {label}"
    )



def cmd_list() -> None:
    collection = data_loader.load_ratings()

    if collection.count() == 0:
        console.print("[yellow]You haven't rated any movies yet.[/yellow]")
        console.print("Run [bold]uv run -m movie_rating_tool add[/bold] to get started.")
        return

    table = Table(
        title=f"Your Movie Ratings ({collection.count()} movies)",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("#",        style="dim",  width=3)
    table.add_column("Title",    style="bold", min_width=25)
    table.add_column("Year",     justify="center")
    table.add_column("Your Score",justify="center")
    table.add_column("Label",    justify="center")
    table.add_column("Rated On", style="dim")
    table.add_column("Review",   style="dim",  max_width=30)


    for i, rating in enumerate(collection.all(), start=1):
        label = rating_engine.get_rating_label(rating.user_score)
        table.add_row(
            str(i),
            rating.title,
            _get_year(rating.movie_id),
            f"[bold green]{rating.user_score}/10[/bold green]",
            label,
            rating.get_date_str(),
            rating.review or "—",
        )

    console.print(table)

# compare user ratings with online ratings

def cmd_compare() -> None:
    collection = data_loader.load_ratings()

    if collection.count() == 0:
        console.print("[yellow]No ratings found. Add some with the 'add' command.[/yellow]")
        return

    df = rating_engine.get_comparison_df(collection)

    if df.empty:
        console.print("[red]Could not build comparison table.[/red]")
        return

    table = Table(
        title="Your Ratings vs Online Ratings",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("Title",          style="bold",  min_width=22)
    table.add_column("Your Score",     justify="center")
    table.add_column("Online Rating",  justify="center")
    table.add_column("Difference",     justify="center")
    table.add_column("Verdict",        justify="center")

    for _, row in df.iterrows():
        diff = row["difference"]

        # Colour the difference: green if user rated higher, red if lower
        if diff > 0:
            diff_str = f"[green]+{diff}[/green]"
            verdict = "You liked it more 👆"
        elif diff < 0:
            diff_str = f"[red]{diff}[/red]"
            verdict = "Others liked it more 👇"
        else:
            diff_str = "[dim]0.0[/dim]"
            verdict = "Perfect match 🎯"

        table.add_row(
            row["title"],
            f"{row['user_score']}/10",
            f"{row['online_rating']}/10",
            diff_str,
            verdict,
        )

    console.print(table)


# show statistics
def cmd_stats() -> None:
    """
    Show statistics about the user's ratings.
    Here we call into that module and display results.
    """
    collection = data_loader.load_ratings()

    if collection.count() == 0:
        console.print("[yellow]No ratings found. Add some with the 'add' command.[/yellow]")
        return

    from movie_rating_tool import analysis

    stats = analysis.compute_stats(collection)

    console.print(Panel(
        f"[bold]📊 Your Rating Statistics[/bold]\n\n"
        f"  Total movies rated : [cyan]{stats['count']}[/cyan]\n"
        f"  Mean score         : [cyan]{stats['mean']}/10[/cyan]\n"
        f"  Median score       : [cyan]{stats['median']}/10[/cyan]\n"
        f"  Highest rated      : [green]{stats['max_title']} ({stats['max_score']})[/green]\n"
        f"  Lowest rated       : [red]{stats['min_title']} ({stats['min_score']})[/red]\n"
        f"  Std deviation      : [cyan]{stats['std']}[/cyan]\n"
        f"  Avg online rating  : [cyan]{stats['mean_online']}/10[/cyan]\n"
        f"  Avg difference     : [cyan]{stats['mean_diff']}[/cyan] "
        f"{'(you rate higher than average)' if stats['mean_diff'] > 0 else '(you rate lower than average)'}",
        border_style="cyan",
    ))

    # Genre breakdown
    if stats.get("genre_counts"):
        console.print("\n[bold]🎭 Genres you've rated:[/bold]")
        for genre, count in stats["genre_counts"].items():
            bar = "█" * count
            console.print(f"  {genre:<20} {bar} {count}")


#visualizations

def cmd_plot() -> None:
    """
    Generate and show visualizations.
    """
    collection = data_loader.load_ratings()

    if collection.count() == 0:
        console.print("[yellow]No ratings found. Add some with the 'add' command.[/yellow]")
        return

    from movie_rating_tool import visualization

    console.print("[bold]📈 Generating plots...[/bold]")
    visualization.plot_all(collection)


# get recommendations
def cmd_recommend() -> None:
    collection = data_loader.load_ratings()

    if collection.count() == 0:
        console.print("[yellow]No ratings found. Add some ratings first![/yellow]")
        return

    console.print("[bold]🎯 Finding recommendations based on your taste...[/bold]\n")

    recommendations = rating_engine.get_recommendations(collection, limit=8)

    if not recommendations:
        console.print("[yellow]Could not generate recommendations.[/yellow]")
        return
    table = Table(
        title="Movies You Might Like",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("#",             style="dim", width=3)
    table.add_column("Title",         style="bold", min_width=25)
    table.add_column("Year",          justify="center")
    table.add_column("Online Rating", justify="center")
    table.add_column("Genres",        style="dim")

    for i, movie in enumerate(recommendations, start=1):
        table.add_row(
            str(i),
            movie["title"],
            str(int(movie["year"])),
            f"⭐ {movie['online_rating']}/10",
            movie["genres"].replace("|", ", "),
        )

    console.print(table)

    console.print(
        "\n[dim]Tip: Run [bold]uv run -m movie_rating_tool add[/bold] "
        "to rate one of these![/dim]"
    )


def _get_year(movie_id: int) -> str:
    """Look up a movie's year from the cache. Returns '—' if not found."""
    movie = data_loader.get_movie_by_id(movie_id)
    if movie:
        return str(int(movie["year"]))
    return "—"