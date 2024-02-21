import pandas as pd
# from imdb import Cinemagoer
from src import embedding_utils
import umap
import numpy as np

# imdb = Cinemagoer()
# movies = [imdb.search_movie('shark')[i] for i in [0, 2, 3]]
# movie_data = pd.DataFrame({'title': [movie['title'] for movie in movies],
#                    'Synopsis': [imdb.get_movie(movie.getID())['plot'][0] for movie in movies]
#                    })
#
# movie_data = embedding_utils.embeddings_dataframe(movie_data)

movie_data = pd.read_csv('data/movie_summaries.csv')
# len(movie_data)

movie_data_split = np.array_split(movie_data, 10)
section_index = 1
for section in movie_data_split:
    embedded = embedding_utils.embeddings_dataframe(section)
    filepath = 'data/movie_embeddings_instructor_' + str(section_index) + '.csv'
    embedded.to_csv(filepath)  # save to csv
    section_index += 1

movie_data = embedding_utils.embeddings_dataframe(movie_data)

