import os

import streamlit as st
import pandas as pd
from umap import UMAP

from src.directories import DATA_DIR


def load_seinfeld_embeddings():
    filepath = DATA_DIR / "seinfeld_embedding_vectors.pkl"
    df = pd.read_pickle(filepath)
    df = df.dropna(axis=0)
    return df


@st.cache_data
def load_movie_summary_embeddings():
    filepath = DATA_DIR / "movie_embeddings_openai.csv"
    df = pd.read_csv(filepath)

    # Reduce
    df.set_index("Movie Title", inplace=True)
    df.drop(columns=["Unnamed: 0.1", "Unnamed: 0", "Movie URL"], inplace=True)
    df.dropna(axis=0, inplace=True)

    synopses = df["Synopsis"].copy()
    embeddings = df.drop(columns=["Synopsis"])
    return synopses, embeddings


def reduce_dimensions(embeddings_df, num_dimensions=20,
                      n_neighbors=17, min_dist=0.3):
    filename = f"movie_synopses-{num_dimensions}_dims.pkl"
    filepath = DATA_DIR / "synopses_embeddings" / filename

    if os.path.exists(filepath):
        reduced = pd.read_pickle(filepath)

    else:
        embeddings = embeddings_df.values
        model = UMAP(n_neighbors=n_neighbors, min_dist=min_dist,
                     n_components=num_dimensions, random_state=42)
        reduced = model.fit_transform(embeddings)
        reduced = pd.DataFrame(index=embeddings_df.index, data=reduced)
        reduced.to_pickle(filepath)

    return reduced



