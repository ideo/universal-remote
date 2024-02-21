import streamlit as st
from scipy import spatial
import numpy as np

from app import logic as lg



st.set_page_config(page_icon="🎤",
                   page_title="Seinfeld Searcher",
                   layout="centered",)

st.title("Seinfeld")
df = lg.load_data()
episodes = df.index.tolist()

TREE = spatial.KDTree(df.values)

col1, _plus, col2 = st.columns([5,1,5])
# , _equals, col3 = st.columns([5,2,5,2,5])

with col1:
    ep1 = st.selectbox("Select an Episode", options=episodes, key="one")

with _plus:
    st.markdown("#### +")

with col2:
    ep2 = st.selectbox("Select an Episode", options=episodes, key="two")

# with _equals:
#     st.markdown("#### =")

# with col3:
_, cntr, _ = st.columns([2,5,2])
with cntr:
    # _sum = df.loc[ep1].values + df.loc[ep2].values
    v1, v2 = df.loc[ep1].values, df.loc[ep2].values
    _mean = np.mean(np.array([v1, v2]), axis=0)
    distances, indices = TREE.query(_mean, k=3)
    episode_names = [df.iloc[ii].name for ii in indices]
    episode_names = [ep for ep in episode_names if ep not in [ep1, ep2]]
    st.write(episode_names[0])

    # st.write(distances, indices)
    # st.write(df.iloc[indices[0]].name)


    # st.write(df.iloc[ii].name)