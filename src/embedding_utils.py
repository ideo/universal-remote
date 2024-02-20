import transformers
import sentence_transformers
from InstructorEmbedding import INSTRUCTOR
import pandas as pd
import umap
import math

# gets a single list of embeddings for one movie
def get_embedding_instructor(text, model):
    instruction = "Represent the Movie paragraph:"
    embedding = model.encode([[instruction, text]])
    return embedding

# def get_embedding_openai(text, model):
# TODO!!!

# iterates through a data frame of movies to grab embeddings and returns dataframe with all info and embeddings
# then returns original data with embedding dimensions
def embeddings_dataframe(movie_data):
    # movie_data = movie_df[(movie_df['Synopsis'] != '') & (movie_df['Synopsis'].notna())]  # remove all movies that don't have a synopsis
    model = INSTRUCTOR('hkunlp/instructor-xl')

    temp_embeddings = []
    for plot in movie_data['Synopsis']:
        print(plot)
        if plot == '' or pd.isna(plot):
            embedding_list = [[None]*768]
        else:
            embedding_list = get_embedding_instructor(plot, model)
            # TODO: make openai/instructor an argument. will need to cat all lists of dims into another list and convert to dataframe
        print(len(embedding_list))
        temp_embeddings.append(embedding_list)

    try:
        temp_embeddings = pd.DataFrame([embeddings[0] for embeddings in temp_embeddings])
    except Exception as error:
        print(error)

    print("created embeddings dataframe")

    ndim = len(temp_embeddings.columns)
    dim_colnames = ['dim' + str(num + 1) for num in range(ndim)]
    new_colnames = [col for col in movie_data.columns] + dim_colnames

    movie_data = pd.concat([movie_data.reset_index(drop = True), temp_embeddings.reset_index(drop = True)],
                           axis = 1, ignore_index = True)
    movie_data.columns = new_colnames
    return movie_data

# once you have a dataframe from embeddings_dataframe, use this to reduce embedding dimensions
def reduce_embeddings(embeddings_df, n_dim = 3, n_neighbors = 17, min_dist = 0.3, n_components = 3, random_state = None):
    just_embeddings = embeddings_df.iloc[:,2:]

    # TODO: turn this into a function where you can manipulate these params and get the combined df
    reduced_embeddings = umap.UMAP(n_neighbors = n_neighbors,  # 17 and 0.3 looked best so far
                                               min_dist = min_dist,
                                               n_components = n,
                                               random_state = 433).\
        fit_transform(just_embeddings)
    reduced_embeddings = pd.DataFrame(reduced_embeddings)

    reduced_df = pd.concat([embeddings_df.loc[0:1], reduced_embeddings])
    reduced_df.columns = [embeddings_df.columns[0:1], 'dim1', 'dim2', 'dim3']

    return reduced_df
