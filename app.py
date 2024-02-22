import streamlit as st

from app import logic as lg


st.set_page_config(
    page_title="Movie Searcher", 
    page_icon="🎬",
    layout="wide")


_, cntr, _ = st.columns([2,5,2])
with cntr:
    st.title("Movie Searcher")


synopses, embeddings = lg.load_movie_summary_embeddings()
embeddings = lg.reduce_dimensions(embeddings)
# st.write(embeddings.values[0])

col1, col2 = st.columns(2)
for col_ii in embeddings.columns:
    descriptors = lg.load_dimension_descriptors()
    dscrptr = descriptors[col_ii]
    if col_ii%2==0:
        with col1:
            lg.dimension_slider(embeddings, col_ii, dscrptr)
    else:
        with col2:
            lg.dimension_slider(embeddings, col_ii, dscrptr)


tree = lg.build_kd_tree(embeddings)
vector = lg.parse_input_vector(embeddings)

print(embeddings.values[0].shape)
print(embeddings.values[0])
print(type(embeddings.values[0]))
movies = lg.find_nearest_neighbors(tree, vector, embeddings)