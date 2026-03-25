# __main__.py
# This file allows the package to be run with:
#   uv run -m movie_rating_tool

from movie_rating_tool.cli import run_cli

def main():
    run_cli()

if __name__ == "__main__":
    main()