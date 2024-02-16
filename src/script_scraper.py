from string import ascii_uppercase
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd

from directories import DATA_DIR


FILEPATH = DATA_DIR / "movie_scripts.csv"
BASE_URL = "https://imsdb.com/"    


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features="html.parser")
    return soup


def create_index():
    df = pd.DataFrame(columns=["Movie Title", "Movie URL"])

    for character in ascii_uppercase + "0":
        # Get page source
        url = urljoin(BASE_URL, f"alphabetical/{character}")
        soup = get_soup(url)

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

        df.to_csv(FILEPATH)
        print(f"{character} ✓")


def get_script(movie_url):
    soup = get_soup(movie_url)

    script_link = soup.select_one("p a[href]")

    if script_link is not None:
        script_link = urljoin(BASE_URL, script_link["href"])
        
        soup = get_soup(script_link)
        script = soup.select_one("pre")
        if script is not None:
            script = script.get_text()
        
        print(f"{movie_url} ✓")
        return script
    
    else:
        return None


if __name__ == "__main__":
    create_index()

    df = pd.read_csv(FILEPATH)
    df["Script"] = df["Movie URL"].apply(get_script)
    df.to_csv(FILEPATH)