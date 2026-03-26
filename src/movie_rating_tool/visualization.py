# visualization.py
# All visualizations for the Movie Rating Tool.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

from movie_rating_tool.models import RatingCollection
from movie_rating_tool import rating_engine, analysis


# Global style settings

sns.set_theme(style="darkgrid", palette="muted")

FIGURE_SIZE = (10, 6)


def plot_all(collection: RatingCollection) -> None:
    """
    Generate and display all visualizations one by one.
    Each chart opens in its own window.
    Args:
        collection : the user's RatingCollection
    """
    print("📊 Chart 1/4 — Rating Comparison")
    plot_rating_comparison(collection)

    print("📊 Chart 2/4 — Score Distribution")
    plot_score_distribution(collection)

    print("📊 Chart 3/4 — Genre Analysis")
    plot_genre_analysis(collection)

    print("📊 Chart 4/4 — User vs Online Scatter")
    plot_scatter(collection)

    print("✅ All charts displayed.")


# Chart 1, Rating comparison bar chart
def plot_rating_comparison(collection: RatingCollection) -> None:
    """
    Grouped bar chart comparing the user's score vs the online rating
    for each movie the user has rated.
    """
    df = rating_engine.get_comparison_df(collection)

    if df.empty:
        print("⚠️  No data to plot.")
        return

    df = df.dropna(subset=["online_rating"])

    titles = [t if len(t) <= 20 else t[:18] + "…" for t in df["title"]]

    x = np.arange(len(titles))
    bar_width = 0.35

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)


    bars_user   = ax.bar(x - bar_width / 2, df["user_score"],    bar_width,
                         label="Your Score",    color="#4C9BE8", alpha=0.9)
    bars_online = ax.bar(x + bar_width / 2, df["online_rating"], bar_width,
                         label="Online Rating", color="#E87B4C", alpha=0.9)


    for bar in bars_user:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            f"{height:.1f}",
            ha="center", va="bottom", fontsize=8, color="#4C9BE8"
        )

    for bar in bars_online:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            f"{height:.1f}",
            ha="center", va="bottom", fontsize=8, color="#E87B4C"
        )

    ax.set_title("Your Ratings vs Online Ratings", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Movie", fontsize=11)
    ax.set_ylabel("Rating (out of 10)", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(titles, rotation=30, ha="right", fontsize=9)
    ax.set_ylim(0, 11)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.legend(fontsize=10)
    ax.set_facecolor("#1e1e2e")
    fig.patch.set_facecolor("#13131f")



    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    ax.legend(facecolor="#2a2a3e", labelcolor="white")

    plt.tight_layout()
    plt.show()


# Chart 2, Score distribution histogram
def plot_score_distribution(collection: RatingCollection) -> None:
    """
    Histogram showing the distribution of the user's scores
    overlaid with a KDE (kernel density estimate) curve.
    """

    scores = np.array([r.user_score for r in collection.all()])

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)


    sns.histplot(
        scores,
        bins=10,
        kde=True,
        color="#4C9BE8",
        ax=ax,
        edgecolor="white",
        linewidth=0.5,
    )


    mean_score = float(np.mean(scores))
    ax.axvline(
        mean_score,
        color="#E87B4C",
        linestyle="--",
        linewidth=1.8,
        label=f"Mean: {mean_score:.1f}",
    )


    median_score = float(np.median(scores))
    ax.axvline(
        median_score,
        color="#4CE87B",
        linestyle=":",
        linewidth=1.8,
        label=f"Median: {median_score:.1f}",
    )

    ax.set_title("Distribution of Your Scores", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Score (out of 10)", fontsize=11)
    ax.set_ylabel("Number of Movies", fontsize=11)
    ax.set_xlim(0, 10)
    ax.legend(fontsize=10)
    ax.set_facecolor("#1e1e2e")
    fig.patch.set_facecolor("#13131f")

    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    ax.legend(facecolor="#2a2a3e", labelcolor="white")

    plt.tight_layout()
    plt.show()


# Chart 3, Genre average scores

def plot_genre_analysis(collection: RatingCollection) -> None:
    """
    Horizontal bar chart showing your average score vs the online
    average rating, grouped by genre.
    """
    genre_df = analysis.get_genre_stats(collection)

    if genre_df.empty:
        print("⚠️  Not enough genre data to plot.")
        return

    genre_df = genre_df[genre_df["count"] >= 1]

    # Limit to top 10 genres so the chart isn't too crowded
    genre_df = genre_df.head(10)

    # Melt the DataFrame from wide to long format for grouped bar chart
    # Before melt:  genre | avg_user_score | avg_online_rating
    # After melt:   genre | variable       | value
    melted = genre_df.melt(
        id_vars="genre",
        value_vars=["avg_user_score", "avg_online_rating"],
        var_name="Rating Type",
        value_name="Score",
    )


    melted["Rating Type"] = melted["Rating Type"].replace({
        "avg_user_score":    "Your Score",
        "avg_online_rating": "Online Rating",
    })

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    sns.barplot(
        data=melted,
        y="genre",
        x="Score",
        hue="Rating Type",
        palette={"Your Score": "#4C9BE8", "Online Rating": "#E87B4C"},
        ax=ax,
        orient="h",
    )


    ax.set_title("Average Scores by Genre", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Average Score (out of 10)", fontsize=11)
    ax.set_ylabel("Genre", fontsize=11)
    ax.set_xlim(0, 10)
    ax.set_facecolor("#1e1e2e")
    fig.patch.set_facecolor("#13131f")

    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    ax.legend(facecolor="#2a2a3e", labelcolor="white", title_fontsize=9)

    plt.tight_layout()
    plt.show()


# Chart 4, Scatter plot: user score vs online rating
def plot_scatter(collection: RatingCollection) -> None:
    """
    Scatter plot of user score (y-axis) vs online rating (x-axis).
    Each dot is a movie. A diagonal line shows where they'd be equal.

    Points above the line = you liked it more than the community.
    Points below the line = the community liked it more than you.
    """
    df = rating_engine.get_comparison_df(collection)

    if df.empty or len(df) < 2:
        print("⚠️  Need at least 2 rated movies for the scatter plot.")
        return

    df = df.dropna(subset=["online_rating"])

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Draw the scatter points
    scatter = ax.scatter(
        df["online_rating"],
        df["user_score"],
        c=df["difference"],
        cmap="coolwarm",
        s=100,
        alpha=0.85,
        edgecolors="white",
        linewidths=0.5,
        zorder=3,
    )


    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Difference (Your − Online)", color="white", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")


    line_vals = np.linspace(0, 10, 100)
    ax.plot(line_vals, line_vals, "--", color="white", alpha=0.4,
            linewidth=1.2, label="Perfect agreement")


    for _, row in df.iterrows():
        short_title = row["title"] if len(row["title"]) <= 15 else row["title"][:13] + "…"
        ax.annotate(
            short_title,
            (row["online_rating"], row["user_score"]),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=7,
            color="white",
            alpha=0.8,
        )

    ax.set_title(
        "Your Score vs Online Rating\n(above the line = you liked it more)",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Online Rating (out of 10)", fontsize=11)
    ax.set_ylabel("Your Score (out of 10)", fontsize=11)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.legend(fontsize=9)
    ax.set_facecolor("#1e1e2e")
    fig.patch.set_facecolor("#13131f")

    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    ax.legend(facecolor="#2a2a3e", labelcolor="white")

    plt.tight_layout()
    plt.show()