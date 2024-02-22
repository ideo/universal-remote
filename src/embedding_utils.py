import transformers
import sentence_transformers
from InstructorEmbedding import INSTRUCTOR
import pandas as pd
import umap
import math
import dotenv
import openai

# gets a single list of embeddings for one movie
def get_embedding_instructor(text, model):
    instruction = "Represent the Movie paragraph:"
    embedding = model.encode([[instruction, text]])
    return embedding

def get_embedding_openai(text, client):
    embedding = client.embeddings.create(input = text, model = 'text-embedding-3-small').data[0].embedding
    return embedding

# iterates through a data frame of movies to grab embeddings and returns dataframe with all info and embeddings
# then returns original data with embedding dimensions
def embeddings_dataframe(movie_data, llm = 'instructor'):  # model can be instructor or openai
    if llm == 'instructor':
        model = INSTRUCTOR('hkunlp/instructor-xl')
    elif llm == 'openai':
        dotenv.load_dotenv()
        model = openai.OpenAI()

    temp_embeddings = []
    for plot in movie_data['Synopsis']:
        print(plot)
        if plot == '' or pd.isna(plot):  # return list of nones if missing plot
            if llm == 'instructor':
                embedding_list = [[None]*768]
            elif llm == 'openai':
                embedding_list = [None]*768
        else:
            if llm == 'instructor':
                embedding_list = get_embedding_instructor(plot, model)
            elif llm == 'openai':
                embedding_list = get_embedding_openai(plot, model)  # not done with this

        print(len(embedding_list))
        temp_embeddings.append(embedding_list)

    if llm == 'instructor':
        try:
            temp_embeddings = pd.DataFrame([embeddings[0] for embeddings in temp_embeddings])
        except Exception as error:
            print(error)
    elif llm == 'openai':
        temp_embeddings = pd.DataFrame(temp_embeddings)

    print("created embeddings dataframe")

    ndim = len(temp_embeddings.columns)
    dim_colnames = ['dim' + str(num + 1) for num in range(ndim)]
    new_colnames = [col for col in movie_data.columns] + dim_colnames

    movie_data = pd.concat([movie_data.reset_index(drop = True), temp_embeddings.reset_index(drop = True)],
                           axis = 1, ignore_index = True)
    movie_data.columns = new_colnames
    return movie_data

# once you have a dataframe from embeddings_dataframe, use this to reduce embedding dimensions
def reduce_embeddings(embeddings_df, n_dim = 3, n_neighbors = 17, min_dist = 0.1, random_state = None):
    just_embeddings = embeddings_df.filter(regex = 'dim')

    # TODO: turn this into a function where you can manipulate these params and get the combined df
    reduced_embeddings = umap.UMAP(n_neighbors = n_neighbors,  # 17 and 0.3 looked best so far
                                               min_dist = min_dist,
                                               n_components = n_dim,
                                               random_state = 433).\
        fit_transform(just_embeddings)
    reduced_embeddings = pd.DataFrame(reduced_embeddings)

    reduced_df = pd.concat([embeddings_df[['Movie Title', 'Movie URL', 'Synopsis']].reset_index(drop = True),
                            reduced_embeddings.reset_index(drop = True)], axis = 1)
    dims = ['dim' + str(dim + 1) for dim in range(n_dim)]
    reduced_df.columns = ['Movie Title', 'Movie URL', 'Synopsis'] + dims

    return reduced_df

def word_wrap(string, n_chars):
    return '\n'.join(string[i:i+n_chars] for i in range(0, len(string), n_chars))
