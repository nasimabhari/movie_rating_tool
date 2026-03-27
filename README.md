# 🎬 Movie Rating Tool

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Dataset](https://img.shields.io/badge/Dataset-MovieLens%20Small-orange)

A Python command-line tool that lets you rate movies, compare your
personal scores with community ratings, explore statistics, and get
personalized recommendations, all from your terminal.

Built as a Python course final project by [@nasimabhari](https://github.com/nasimabhari).

---

## ✨ Features

| Feature      | Description                                       |
| ------------ | ------------------------------------------------- |
| 🔍 Search    | Search 9,742 movies from the MovieLens dataset    |
| ⭐ Rate      | Add personal ratings (0–10) with optional reviews |
| 📊 Compare   | Side-by-side: your score vs community rating      |
| 📈 Stats     | Mean, median, std deviation, genre breakdown      |
| 🎨 Visualize | 4 charts: bar, histogram, genre analysis, scatter |
| 🎯 Recommend | Personalized recommendations based on your taste  |

---

## 🛠️ Tech Stack

| Library        | Used For                                                |
| -------------- | ------------------------------------------------------- |
| **Pandas**     | Data loading, CSV storage, merging datasets             |
| **NumPy**      | Statistical calculations (mean, median, std, histogram) |
| **Matplotlib** | Bar charts, scatter plots, histograms                   |
| **Seaborn**    | Styled histogram with KDE, genre bar chart              |
| **Rich**       | Beautiful terminal output (tables, panels, colours)     |

---

## 📦 Installation

Make sure you have [uv](https://docs.astral.sh/uv/) installed.

```bash
# Clone the repository
git clone https://github.com/nasimabhari/movie_rating_tool.git
cd movie-rating-tool

# Run directly — uv handles everything automatically
uv run -m movie_rating_tool
```

That's it! On the first run, the MovieLens dataset (~1MB) is downloaded
and cached automatically.

---

## 🚀 Usage

```bash
# Show the command menu
uv run -m movie_rating_tool

# Search for a movie
uv run -m movie_rating_tool search

# Add a personal rating
uv run -m movie_rating_tool add

# List all your ratings
uv run -m movie_rating_tool list

# Compare your ratings with community ratings
uv run -m movie_rating_tool compare

# Show statistics (mean, median, genres, etc.)
uv run -m movie_rating_tool stats

# Show visualizations
uv run -m movie_rating_tool plot

# Get movie recommendations
uv run -m movie_rating_tool recommend
```

---

## 📁 Project Structure

```
movie_rating_tool/
│
├── pyproject.toml          # Package config (no setup.py!)
├── README.md
├── .gitignore
│
├── data/
│   ├── ml-latest-small/    # MovieLens dataset (included, ~1MB)
│   │   ├── movies.csv
│   │   └── ratings.csv
│   └── movies_cache.csv    # Auto-generated cache
│
├── notebooks/
│   └── movie_rating_tool_demo.ipynb  # Full demo notebook
│
└── src/
    └── movie_rating_tool/
        ├── __init__.py       # Package marker + version
        ├── __main__.py       # Entry point (uv run -m ...)
        ├── cli.py            # All CLI commands
        ├── models.py         # Movie, UserRating, RatingCollection
        ├── data_loader.py    # CSV storage + dataset loading
        ├── rating_engine.py  # Comparison + recommendations
        ├── analysis.py       # NumPy + Pandas statistics
        └── visualization.py  # Matplotlib + Seaborn charts
```

---

## 📓 Jupyter Notebook

A full demo notebook is available at `notebooks/movie_rating_tool_demo.ipynb`.

```bash
uv run jupyter notebook notebooks/movie_rating_tool_demo.ipynb
```

---

## 📄 Data Source

This project uses the [MovieLens Small Dataset](https://grouplens.org/datasets/movielens/latest/)
provided by GroupLens Research at the University of Minnesota.

- 9,742 movies
- 100,836 ratings from 610 users
- Ratings scaled from 0.5–5.0 → 0–10 for this project

---

## 👤 Author

**Nasim Abhari** — [@nasimabhari](https://github.com/nasimabhari)
