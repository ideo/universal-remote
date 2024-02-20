from src import DATA_DIR
from src.script_scraper import Script_Scraper


filepath = DATA_DIR / "seinfeld_scripts.csv"
scraper = Script_Scraper()
scraper.seinfeld(filepath)

