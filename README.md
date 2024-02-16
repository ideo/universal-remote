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