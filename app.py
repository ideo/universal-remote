import streamlit as st

from app import logic as lg


st.set_page_config(
    page_title="Movie Searcher", 
    page_icon="🎬",
    layout="wide")

config = lg.load_config_file()

_, cntr, _ = st.columns([2,5,2])
with cntr:
    st.title("Movie Searcher")    
    lg.write_text(config, "introduction", header_level=None)
    lg.write_text(config, "How it Works", header_level=3)
    
    


synopses, embeddings = lg.load_movie_summary_embeddings()
embeddings = lg.reduce_dimensions(embeddings, num_dimensions=10)

with st.expander("Movie Toggles", expanded=True):
    col1, col2 = st.columns(2)
    for col_ii in embeddings.columns:
        descriptors = lg.load_dimension_descriptors(config)
        dscrptr = descriptors[col_ii]
        if col_ii%2==0:
            with col1:
                lg.dimension_slider(embeddings, col_ii, dscrptr)
        else:
            with col2:
                lg.dimension_slider(embeddings, col_ii, dscrptr)


tree = lg.build_kd_tree(embeddings)
vector = lg.parse_input_vector(embeddings)
movie_names = lg.find_nearest_neighbors(tree, vector, embeddings, n_neighbors=20)

_, col1, col2, _ = st.columns([2,2,2,2])
with col1:
    for movie in movie_names[0:10]:
        st.markdown(f"**{movie}**")
with col2:
    for movie in movie_names[10:]:
        st.markdown(f"**{movie}**")

_, cntr, _ = st.columns([2,5,2])
with cntr:
    st.write("")
    with st.expander("Read the plot summaries that informed the model.", expanded=False):
        st.table(synopses.loc[movie_names])

    st.markdown("---")
    lg.write_text(config, "How to Improve Upon This", header_level=3)
    lg.write_text(config, "Better Data", header_level=5)
    lg.write_text(config, "Better Spectrums", header_level=5)


