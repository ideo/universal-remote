import os

from string import ascii_uppercase
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

from ..directories import DATA_DIR


tqdm.pandas()
FILEPATH = DATA_DIR / "movie_scripts.csv"
BASE_URL = "https://imsdb.com/"    


class Script_Scraper:
    def __init__(self):
        self.base_url = BASE_URL


    def seinfeld(self, filepath):
        # Episode Index
        df = self._load_dataframe_if_exists(filepath)
        if df is None:
            df = self._get_seinfeld_episode_link(df)

        # Get Episode Scripts
        df["Script"] = df["Episode Page"].progress_apply(
            lambda url: self.get_script_from_episode_page(url)
        )

        df.to_csv(filepath)
        return df
        
    
    def _get_seinfeld_episode_link(self, df):
        """Scrape the list of episodes and script page links"""  
        episode_list = urljoin(self.base_url, "TV/Seinfeld.html")
        soup = self.make_soup(episode_list)
        episode_links = soup.select("p a[href]")

        desc = "Getting Episode Index"
        for ii, link in enumerate(tqdm(episode_links, desc=desc)):
            data = {
                "Episode Title":    link.get_text(),
                "Episode Page":      urljoin(BASE_URL, link["href"]),
                }
            df = pd.concat([df, pd.DataFrame(data, index=[ii])])

        return df


    ### Scraper Utils ###
            
    def make_soup(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, features="html.parser")
        return soup
    

    def _load_dataframe_if_exists(self, filepath):
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            return df
        else:
            return None
        

    def get_script_from_episode_page(self, movie_or_episode_url):
        soup = self.make_soup(movie_or_episode_url)

        script_link = soup.select_one("p a[href]")

        if script_link is not None:
            script_link = urljoin(BASE_URL, script_link["href"])
            
            soup = self.make_soup(script_link)
            script = soup.select_one("pre")
            if script is not None:
                script = script.get_text()
            
            # print(f"{movie_or_episode_url} ✓")
            return script
        
        else:
            return None


#################


def create_index():
    df = pd.DataFrame(columns=["Movie Title", "Movie URL"])

    for character in ascii_uppercase + "0":
        # Get page source
        url = urljoin(BASE_URL, f"alphabetical/{character}")
        soup = stir_up_some_soup_baebae(url)

        # Grab Links
        all_links = soup.select("p a[href]")
        script_links = [
            {
                "Movie URL":  urljoin(BASE_URL, a_tag["href"]), 
                "Movie Title": a_tag["title"].replace(" Script", "").strip(),
            } 
            for a_tag in all_links]
        
        temp_df = pd.DataFrame(script_links)
        df = pd.concat([df, temp_df])

        # df.to_csv(FILEPATH)
        print(f"{character} ✓")
    return df








if __name__ == "__main__":
    create_index()

    df = pd.read_csv(FILEPATH)
    df["Script"] = df["Movie URL"].apply(get_script)
    df.to_csv(FILEPATH)