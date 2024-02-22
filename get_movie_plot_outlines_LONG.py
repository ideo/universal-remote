"""
For each movie in the Internet Movie Script Database, this queries IMDB - the 
regular one, not the script one - for the plot summary.
"""
import os

import numpy as np
import pandas as pd

from src import DATA_DIR
from src.script_scraper import imdb_scraper
from src.script_scraper import script_database_scraper


FILEPATH_SHORT = DATA_DIR / "movie_summaries.csv"
FILEPATH_LONG = DATA_DIR / "movie_summaries_LONG.csv"

# Get List of Movies
if not os.path.exists(FILEPATH_LONG):
    df = pd.read_csv(FILEPATH_SHORT)
    df = df[['Movie Title', 'Movie URL']]
    df["Synopsis"] = np.nan
    df.to_csv(FILEPATH_LONG)
else:
    df = pd.read_csv(FILEPATH_LONG)


# Get Plot Summaries
df.set_index("Movie Title", inplace=True)
for title in df.index:
    if not isinstance(df.loc[title, "Synopsis"], str):
        df.loc[title, "Synopsis"] = imdb_scraper.get_long_synopsis(title)
        df.to_csv(FILEPATH_LONG)