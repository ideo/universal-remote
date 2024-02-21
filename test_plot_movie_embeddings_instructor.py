import pandas as pd
from src import embedding_utils
import plotly.express as px
import textwrap

# TODO: replace this with the code that gets all the filenames that start with the pattern
movie_data = pd.concat([pd.read_csv('data/movie_embeddings_instructor_1.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_2.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_3.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_4.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_5.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_6.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_7.csv'),
                        pd.read_csv('data/movie_embeddings_instructor_8.csv')],
                       axis = 0)
movie_data = movie_data[movie_data['dim1'].notna()]
movie_data = movie_data[movie_data.columns.drop(list(movie_data.filter(regex = 'Unnamed')))]

reduced_data = embedding_utils.reduce_embeddings(movie_data)
reduced_data['Synopsis_wrapped'] = reduced_data.apply([lambda row: '<br>'.join(textwrap.wrap(row['Synopsis'], 60))], axis = 1)

plot = px.scatter_3d(reduced_data, x = 'dim1', y = 'dim2', z = 'dim3',
                     hover_data = ['Movie Title', 'Synopsis_wrapped'],
                     opacity = 0.7)

plot.show()