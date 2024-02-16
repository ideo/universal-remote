import transformers
import sentence_transformers
from InstructorEmbedding import INSTRUCTOR
import pandas as pd

# gets a single list of embeddings for one movie
def get_embedding(text):
    model = INSTRUCTOR('hkunlp/instructor-xl')
    instruction = "Represent the Movie paragraph:"
    embedding = model.encode([[instruction, text]])
    return embedding

# iterates through a data frame of movies to grab embeddings and returns dataframe with all info and embeddings
# then saves as
def embeddings_dataframe(movie_df):
    temp_embeddings = []
    for plot in movie_df['Synopsis']:
        embedding_list = get_embedding(plot)
        temp_embeddings.append(embedding_list)
    temp_embeddings = pd.DataFrame([embeddings[0] for embeddings in temp_embeddings])

    ndim = len(temp_embeddings.columns)
    dim_colnames = ['dim' + str(num + 1) for num in range(ndim)]
    new_colnames = [col for col in movie_df.columns] + dim_colnames

    movie_data = pd.concat([movie_df, temp_embeddings], axis = 1, ignore_index = True)
    movie_data.columns = new_colnames
    return movie_data

