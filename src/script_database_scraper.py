from string import ascii_uppercase
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd

from .directories import DATA_DIR


FILEPATH = DATA_DIR / "movie_scripts.csv"
BASE_URL = "https://imsdb.com/"    


def stir_up_some_soup_baebae(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features="html.parser")
    return soup


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


def get_script(movie_url):
    soup = stir_up_some_soup_baebae(movie_url)

    script_link = soup.select_one("p a[href]")

    if script_link is not None:
        script_link = urljoin(BASE_URL, script_link["href"])
        
        soup = stir_up_some_soup_baebae(script_link)
        script = soup.select_one("pre")
        if script is not None:
            script = script.get_text()
        
        print(f"{movie_url} ✓")
        return script
    
    else:
        return None


def scrape_seinfeld_scripts(filepath):
    seinfeld_url = "https://imsdb.com/TV/Seinfeld.html"
    soup = stir_up_some_soup_baebae(seinfeld_url)

    df = pd.DataFrame(columns=["Episode Title", "Script"])
    episode_links = soup.select("p a[href]")

    for ii, link in enumerate(episode_links):
        data = {"Episode Title": link.get_text()}
        df = pd.concat([df, pd.DataFrame(data, index=[ii])])

        script_page = urljoin(BASE_URL, link["href"])

        df.to_csv(filepath)


if __name__ == "__main__":
    create_index()

    df = pd.read_csv(FILEPATH)
    df["Script"] = df["Movie URL"].apply(get_script)
    df.to_csv(FILEPATH)