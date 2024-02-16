from src import DATA_DIR, script_database_scraper


filepath = DATA_DIR / "seinfeld_scripts.csv"
script_database_scraper.scrape_seinfeld_scripts(filepath)