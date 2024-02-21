import streamlit as st

from app import logic as lg


st.set_page_config(page_title="Movie Searcher", page_icon="🎬")
st.title("Movie Searcher")


synopses, embeddings = lg.load_movie_summary_embeddings()
embeddings = lg.reduce_dimensions(embeddings)
st.write(embeddings)