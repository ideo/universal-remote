"""
For each movie in the Internet Movie Script Database, this queries IMDB - the 
regular one, not the script one - for the plot summary.
"""
import os

import numpy as np
import pandas as pd

from src import DATA_DIR
from src import script_database_scraper, imdb_scraper


FILEPATH = DATA_DIR / "movie_summaries.csv"

# Get List of Movies
if not os.path.exists(FILEPATH):
    df = script_database_scraper.create_index()
    df["Synopsis"] = np.nan
    df.to_csv(FILEPATH)

else:
    df = pd.read_csv(FILEPATH)


# Get Plot Summaries
df.set_index("Movie Title", inplace=True)
for title in df.index:
    if not isinstance(df.loc[title, "Synopsis"], str):
        df.loc[title, "Synopsis"] = imdb_scraper.get_synopsis(title)
        df.to_csv(FILEPATH)