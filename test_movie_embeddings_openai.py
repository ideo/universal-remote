import pandas as pd
from src import embedding_utils
import numpy as np
import openai
import dotenv

movie_data = pd.read_csv('data/movie_summaries.csv')
# movie_data = movie_data.iloc[0:10]

embedded = embedding_utils.embeddings_dataframe(movie_data, 'openai')
print(embedded)

embedded.to_csv('data/movie_embeddings_openai.csv')