import streamlit as st
import pandas as pd

from src.directories import DATA_DIR


def load_data():
    filepath = DATA_DIR / "seinfeld_embedding_vectors.pkl"
    df = pd.read_pickle(filepath)
    df = df.dropna(axis=0)
    return df


# def add_vectors(v1, v2):
