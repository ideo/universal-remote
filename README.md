# universal-remote

### Use
1. Scrape the all plot summaries from IMDB for each movie in the IM_S_DB with the following. It will save `movie_summaries.csv` to `data/`.
    ```bash
    python get_movie_plot_outlines.py.py
    ```    


### Development
1. This project was built in Python 3.11.4. We recommend using Pyenv to manage Python installations.

1. We use [Poetry](https://python-poetry.org/docs/master/#installation) to manage dependencies, but we have included a `requirements.txt` file as well. Ask poetry to output a `requirements.txt` file for you with:
    ```bash
    poetry export --without-hashes --format=requirements.txt > requirements.txt
    ```

1. I have added all scraper dependencies with:
    ```bash
    poetry add --group scraper [package-name]
    ```
    This will let us keep the dependencies separate and organized, as the scraper may only be needed temporarily.

1. You can use Jupyter Notebooks with Poetry by creating a kernel like so:
    ```bash
    poetry run python -m ipykernel install --user --name [project-name]
    ```
    Start your notebooks with `poetry run jupyter lab` and select your newly created kernel.