# universal-remote

### Use

1. Scrape the Internet Movie Script Database with the following. It will save `movie_scripts.csv` to `data/`.  
    ```base
    python src/script_scraper.py
    ```    


### Development
1. This project was built in Python 3.11.4. We recommend using Pyenv to manage Python installations.

1. We use [Poetry](https://python-poetry.org/docs/master/#installation) to manage dependencies, but we have included a `requirements.txt` file as well. Ask poetry to output a `requirements.txt` file for you with:
    ```bash
    poetry export --without-hashes --format=requirements.txt > requirements.txt
    ```