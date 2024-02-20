import os
import re

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, BadRequestError
from tqdm import tqdm

from src.directories import DATA_DIR


load_dotenv()
tqdm.pandas()


CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
SMALL_MODEL = "text-embedding-3-small"
LARGE_MODEL = "text-embedding-3-large"


def get_seinfeld_embeddings():
    filepath = DATA_DIR / "seinfeld_scripts.csv"
    df = pd.read_csv(filepath)
    df["Cleaned Script"] = df["Script"].apply(clean_script)

    df["Embeddings"] = df["Cleaned Script"].progress_apply(fetch_embeddings_api_call)

    filepath = DATA_DIR / "seinfeld_embeddings.pkl"
    df.to_pickle(filepath)


def fetch_embeddings_api_call(source_text):
    try:
        response = CLIENT.embeddings.create(
            input=source_text,
            model=LARGE_MODEL,
        )
    except BadRequestError:
        return None



def clean_script(script):
    patterns = [
        "([A-Z ]+(\\r\\n)+)", #CHARACTER NAME
        "(\\r\\n)+ *", #carriage returns
        "\s{2,}", #large chunks of spaces
    ]
    replacements = [
        lambda match: match[0].strip(),
        " ",
        " ",
    ]

    for pattern, replacement in zip(patterns, replacements):
        script = re.sub(pattern, replacement, script)

    return script.strip()


if __name__ == "__main__":
    get_seinfeld_embeddings()