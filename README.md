# 🎬 Movie Rating Tool

A Python command-line tool that lets you rate movies, compare your ratings with IMDb scores, explore statistics, and get personalized recommendations.

## Features

- ⭐ Add and store your personal movie ratings
- 📊 Fetch and compare with real IMDb ratings
- 📈 View statistics (mean, median, rating difference)
- 🎨 Beautiful visualizations (bar charts, distributions)
- 🎯 Get movie recommendations based on your taste!

## Tech Stack

- **Python 3.10+**
- **Pandas** — data manipulation
- **NumPy** — statistical calculations
- **Matplotlib / Seaborn** — visualizations
- **Rich** — beautiful terminal output

## Installation

Make sure you have [uv](https://docs.astral.sh/uv/) installed, then:
```bash
git clone https://github.com/nasimabhari/movie_rating_tool.git
cd movie-rating-tool
uv run -m movie_rating_tool
```

## Usage
```bash
# Run the tool
uv run -m movie_rating_tool

# Add a rating
uv run -m movie_rating_tool add

# List your ratings
uv run -m movie_rating_tool list

# Compare with IMDb
uv run -m movie_rating_tool compare

# Show statistics
uv run -m movie_rating_tool stats

# Show visualizations
uv run -m movie_rating_tool plot

# Get recommendations
uv run -m movie_rating_tool recommend
```

## Project Structure
```
movie_rating_tool/
├── pyproject.toml
├── README.md
├── .gitignore
├── data/
├── notebooks/
└── src/
    └── movie_rating_tool/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── models.py
        ├── data_loader.py
        ├── rating_engine.py
        ├── analysis.py
        └── visualization.py
```

## Author

**nasimabhari**