import pandas as pd
import numpy as np
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from scipy import spatial
from src.directories import DATA_DIR, EMBEDDINGS_DIR, APP_DIR


def load_movie_summary_embeddings():
    filepath = DATA_DIR / "movie_synopses_embeddings.pkl"
    df = pd.read_pickle(filepath)


    # Reduce
    df.set_index("Movie Title", inplace=True)
    df.drop(columns=["Movie URL"], inplace=True)  # TODO: this might break w PCA
    df.dropna(axis=0, inplace=True)

    # Split
    synopses = df["Synopsis"].copy()
    embeddings = pd.DataFrame(df["Embeddings"].to_list(), index=df.index)

    return synopses, embeddings

def load_movie_principal_components():
    pca_filepath = DATA_DIR / 'movie_embeddings_pca.pkl'
    pca = pd.read_pickle(pca_filepath)

    synopses = pd.DataFrame(pca['Synopsis'])
    pca = pca.drop(columns = ['Synopsis'])

    return synopses, pca



class Bot:
    def __init__(self, advanced = False):
        self.bot = ChatOpenAI(model_name='gpt-4-turbo-preview')
        self.advanced = advanced
        if self.advanced:
            synopses, pca = load_movie_principal_components()
            self.pca = pca
            pca_melted = pca.reset_index()
            self.pca_melted = pd.melt(pca_melted, id_vars = ['Movie Title'], var_name = 'pc', value_name = 'value')
            self.pca_melted['abs_value'] = self.pca_melted['value'].apply(lambda x: abs(x))
        else:
            synopses, embeddings = load_movie_summary_embeddings()
            self.embeddings = embeddings
            embeddings_df = pd.concat([synopses, embeddings], axis=1)
            self.embeddings_df = embeddings_df[embeddings_df[0].notna()]  # select movies where dims are known
        self.synopses = synopses
        self.messages = []


    def average_embeddings(self, dict_list):
        if self.advanced:  # averages only across most notable PCs for each movie
            titles = [item['movie'] for item in dict_list]
            rows = [self.pca[self.pca.index == item['movie']] for item in dict_list]
            melted_rows = [self.pca_melted[self.pca_melted['Movie Title'] == item['movie']] for item in dict_list]
            melted_rows = pd.concat(melted_rows)
            if len([row for row in rows if row.empty]) > 0:  # make sure at least one movie was identified in our data
                raise Exception('less than 2 of the movies you mentioned were identified in our database!')
            weights = [item['weight'] for item in dict_list]

            # for each movie, get the 2 PCs where the absolute value for the movie is highest
            # note: there are 2 duplicate movies I think that are causing there to be 2 less groups than there are movies
            extreme_pcas_per_movie = (melted_rows.groupby(by='Movie Title').
                                      apply(lambda x: x.nlargest(2, 'abs_value')['pc']))
            extreme_pcas_per_movie = pd.DataFrame(extreme_pcas_per_movie)

            # then, select only the intersection of the PCs where all the movies are most extreme
            pcas_to_consider = list(set(extreme_pcas_per_movie['pc']))
            relevant_query_rows = pd.concat(rows)[pcas_to_consider]
            all_relevant_rows = self.pca[pcas_to_consider]

            # then average the movies (weighted) over those dimensions only
            _mean = np.average(np.array(relevant_query_rows), weights=weights, axis=0)
            TREE = spatial.KDTree(all_relevant_rows)
            distances, indices = TREE.query(_mean, k=5)
            indices = indices.tolist()
            movie_names = [all_relevant_rows.index[ii] for ii in indices]
            movie_names = [ep for ep in movie_names if ep not in titles]

        else:  # average two movies and return closest suggestion
            # TODO: right now we are assuming that everything is spelled the same way as in the database
            titles = [item['movie'] for item in dict_list]
            rows = [self.embeddings[self.embeddings_df.index == item['movie']] for item in dict_list]
            if len([row for row in rows if row.empty]) > 0:  # make sure at least one movie was identified in our data
                raise Exception('less than 2 of the movies you mentioned were identified in our database!')
            weights = [item['weight'] for item in dict_list]
            # print(rows)
            # print(weights)
            _mean = np.average(np.array(rows), weights=weights, axis=0)

            TREE = spatial.KDTree(self.embeddings)
            distances, indices = TREE.query(_mean, k=5)
            indices = indices.tolist()[0]
            movie_names = [self.embeddings.index[ii] for ii in indices]
            movie_names = [ep for ep in movie_names if ep not in titles]

        return movie_names





    def process_input(self, user_input = None):  # processes user's initial message
        if user_input is None:
            user_input = input('What would you like to watch today?')
        self.messages.append(  # TODO: use ChatMessageHistory instead
            SystemMessage(content=
                          """ 
                            Return a Python list of dictionaries. There should be one dictionary for each movie the user mentions. 
                            Each dictionary should have the following key/value pairs:
                            The value of the key "movie" should state a movie mentioned by the user, spelled exactly as the user did. 
                            The value of all of the "weight" keys should add up to 1. 
                            If the user asks for a simple average or "cross between" a list of movies, 
                            the weight should be distributed evenly across all movies.
                            Otherwise, if the user suggests that one movie should be weighted heavier or lighter, interpret their
                            words and adjust the weights accordingly.
                            For instance, if the user says "I want to watch a movie like Movie A but a little more like Movie B", 
                            an appropriate weighting would be 0.8 for Movie A and 0.2 for Movie B.
                            Do not format response, output it in plain text.
                        """))
        self.messages.append(HumanMessage(content = user_input))
        response = self.bot.invoke(self.messages)
        self.messages.append(response)
        print(response)
        return eval(response.content)  # TODO: need to do some spelling deviation correction here. can we use movie titles embeddings / search for this?

    # TODO: spit out the recs in plain language
    def give_recs(self, recs):
        self.messages.append(
            SystemMessage("""
                The input message is a Python list of movie titles. 
                You are to recommend these movies in natural language based on their previous query.
                Don't justify the recommendations, just offer them concisely.
            """))
        self.messages.append(HumanMessage(content = str(recs)))
        response = self.bot.invoke(self.messages)
        self.messages.append(response)
        # print(response)
        return response.content
