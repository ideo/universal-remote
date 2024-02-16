import pandas as pd
from imdb import Cinemagoer
import plotly.express as px
from src import embedding_utils
import umap

# movie_data = pd.read_csv('filepath')
imdb = Cinemagoer()
movies = [imdb.search_movie('shark')[i] for i in [0, 2, 3]]
movie_data = pd.DataFrame({'title': [movie['title'] for movie in movies],
                   'Synopsis': [imdb.get_movie(movie.getID())['plot'][0] for movie in movies]
                   })

movie_data = embedding_utils.embeddings_dataframe(movie_data)
just_embeddings = movie_data.iloc[:,2:]

### SORRY turns out we can't test the following yet on a small sample dataset. let's just run it with the whole dataset on tuesday
# reduced_embeddings = umap.UMAP(n_neighbors = 17,  # 17 and 0.3 looked best so far
#                                            min_dist = 0.3,
#                                            n_components = 3,
#                                            random_state = 433).\
#     fit_transform(just_embeddings)
# reduced_embeddings = pd.DataFrame(reduced_embeddings)
#
# reduced_df = pd.concat([movie_data.loc[0:1], reduced_embeddings])
# reduced_df.columns = [movie_data.columns[0:1], 'dim1', 'dim2', 'dim3']
#
# plot = px.scatter_3d(reduced_df, x = 'dim1', y = 'dim2', z = 'dim3',
#                      hover_data = ['Movie Title', 'Synopsis'],
#                      opacity = 0.7)
#
# plot.show()