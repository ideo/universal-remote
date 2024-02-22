import os

import streamlit as st
import pandas as pd
import numpy as np
from umap import UMAP
from scipy import spatial

from src.directories import DATA_DIR, EMBEDDINGS_DIR, APP_DIR
from app import utils


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
    filepath = EMBEDDINGS_DIR / filename

    if os.path.exists(filepath):
        reduced = pd.read_pickle(filepath)

    else:
        # Reduce
        embeddings = embeddings_df.values
        model = UMAP(n_neighbors=n_neighbors, min_dist=min_dist,
                     n_components=num_dimensions, random_state=42)
        reduced = model.fit_transform(embeddings)
        reduced = pd.DataFrame(index=embeddings_df.index, data=reduced)

        reduced.to_pickle(filepath)

    return reduced



def dimension_slider(embeddings, col_ii, descriptor):
    _min, _max = embeddings[col_ii].min(), embeddings[col_ii].max()
    _min, _max = float(_min), float(_max)
    starting_value = np.mean([_min, _max])
    st.slider(label=f"How {descriptor}?",
              min_value=_min, max_value=_max,
              value=starting_value,
              key=f"dimension_slider_{col_ii}",
              format="")
    

def load_dimension_descriptors():
    filepath = APP_DIR / "config.yaml"
    config = utils.load_yaml_file(filepath)
    descriptors = config["dimension descriptors"]
    return descriptors


def build_kd_tree(embeddings):
    filepath = EMBEDDINGS_DIR / f"kd-tree_{embeddings.shape[1]}_dims.pbz2"

    if not os.path.exists(filepath):
        tree = spatial.KDTree(embeddings.values)
        utils.save_gherkin(tree, filepath)
    else:
        tree = utils.load_gherkin(filepath)

    return tree


def parse_input_vector(embeddings):
    key = lambda x: f"dimension_slider_{x}"
    vector = [st.session_state[key(col_ii)] for col_ii in embeddings.columns]
    return vector


def find_nearest_neighbors(tree, vector, n_neghbors=10):
    search_vector = np.array(vector)
    print(search_vector.shape)
    print(search_vector)
    print(type(search_vector))
    neighbors = tree.query(search_vector, k=n_neghbors)
    st.write(neighbors)