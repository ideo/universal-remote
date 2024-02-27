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
    df.drop(columns=["Movie URL"], inplace=True)
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

def clean_movie_string(title):
    title = title.lower()
    cleaned_title_options = [title]  # it could appear normally with the leading "the"
    the_split = title.split('the ')
    if the_split[0] == '':  # if the movie starts with "the", here are some alternative ways it might appear in imdb:
        cleaned_title_options.append('the '.join(the_split[1:]) + ', the')  # comma "the"
        cleaned_title_options.append('the '.join(the_split[1:]))  # without leading "the"
    return cleaned_title_options

class Bot:
    def __init__(self, advanced = False):
        self.bot = ChatOpenAI(model_name='gpt-4-turbo-preview')
        self.advanced = advanced
        if self.advanced:
            synopses, pca = load_movie_principal_components()
            self.pca = pca
            self.pca.index = self.pca.index.str.lower()  # make the titles lowercase for easier search
            pca_melted = pca.reset_index()
            self.pca_melted = pd.melt(pca_melted, id_vars = ['Movie Title'], var_name = 'pc', value_name = 'value')
            self.pca_melted['abs_value'] = self.pca_melted['value'].apply(lambda x: abs(x))
        else:
            synopses, embeddings = load_movie_summary_embeddings()
            synopses.index = synopses.index.str.lower()  # make the titles lowercase for easier search
            embeddings.index = embeddings.index.str.lower()
            self.embeddings = embeddings
            embeddings_df = pd.concat([synopses, embeddings], axis=1)
            self.embeddings_df = embeddings_df[embeddings_df[0].notna()]  # select movies where dims are known
        self.synopses = synopses
        self.messages = []


    def average_embeddings(self, dict_list):
        titles = [item['movie'] for item in dict_list]

        if self.advanced:  # averages only across most notable PCs for each movie
            # TODO: implement fuzzy search
            rows = self.pca.loc[[spelling_option for item in dict_list for
                                 spelling_option in clean_movie_string(item['movie'])
                                 if spelling_option in self.pca.index]]
            melted_rows = [self.pca_melted[self.pca_melted['Movie Title'].isin(clean_movie_string(item['movie']))] for item in dict_list]
            melted_rows = pd.concat(melted_rows)
            if len(rows) < 2:  # make sure at least one movie was identified in our data
                raise Exception('less than 2 of the movies you mentioned were identified in our database!')
            weights = [item['weight'] for item in dict_list]

            # for each movie, get the 2 PCs where the absolute value for the movie is highest (extremes)
            # note: there are 2 duplicate movies I think that are causing there to be 2 less groups than there are movies
            extreme_pcas_per_movie = (melted_rows.groupby(by='Movie Title').
                                      apply(lambda x: x.nlargest(2, 'abs_value')['pc']))
            extreme_pcas_per_movie = pd.DataFrame(extreme_pcas_per_movie.reset_index(level = 1, drop = True))
            extreme_pcas_per_movie = extreme_pcas_per_movie.reset_index().merge(melted_rows, how='left', on=['Movie Title', 'pc'])

            # for each unique combo of movie and PC where there are extreme values across both movies,
            # make a dataframe and get the PC values from the movies where that PC is a top 2 extreme for that movie.
            # This can result in some NA values if the movies did not share the exact same extreme PCs.
            # we will fill those NAs with the value of the same PC from the other movie, implying that we want
            # a recommended movie that is as extreme in that dimension as the other movie.
            pcas_to_consider = list(extreme_pcas_per_movie['pc'].unique())
            special_mean_df = pd.MultiIndex.from_product([
                list(extreme_pcas_per_movie['Movie Title'].unique()),
                pcas_to_consider],
                names = ['Movie Title', 'pc']).to_frame(index=False)
            special_mean_df = pd.DataFrame(special_mean_df.merge(extreme_pcas_per_movie[['Movie Title', 'pc', 'value']], how = 'left'))
            to_fill = special_mean_df[special_mean_df['value'].isnull()][['Movie Title', 'pc']]
            to_fill['Movie Title'] = list(to_fill['Movie Title'][::-1])  # swap movie titles; index special_mean_df with this
            to_fill = to_fill.merge(special_mean_df, 'left')
            to_fill['Movie Title'] = list(to_fill['Movie Title'][::-1])
            special_mean_df = special_mean_df.merge(to_fill.rename(columns={'value': 'value2'}), 'left')
            special_mean_df['value'] = special_mean_df['value'].fillna(special_mean_df['value2'])
            special_mean_df = special_mean_df.drop(columns = ['value2'])
            special_mean_df = special_mean_df.pivot(index='Movie Title', columns='pc', values='value').sort_index(axis=1)

            all_relevant_rows = self.pca[pcas_to_consider].sort_index(axis=1)

            # then average the movies (weighted) over those dimensions only
            _mean = np.average(np.array(special_mean_df), weights=weights, axis=0)
            TREE = spatial.KDTree(all_relevant_rows)
            distances, indices = TREE.query(_mean, k=5)
            indices = indices.tolist()
            movie_names = [all_relevant_rows.index[ii] for ii in indices]
            movie_names = [ep for ep in movie_names if ep not in [option for title in titles for option in clean_movie_string(title)]]


        else:  # average two movies and return closest suggestion
            rows = self.embeddings.loc[[spelling_option for item in dict_list for  # TODO: needs testing
                                 spelling_option in clean_movie_string(item['movie'])
                                 if spelling_option in self.embeddings.index]]
            if len(rows) < 2:  # make sure at least one movie was identified in our data
                raise Exception('less than 2 of the movies you mentioned were identified in our database!')
            weights = [item['weight'] for item in dict_list]
            # print(rows)
            # print(weights)
            _mean = np.average(np.array(rows), weights=weights, axis=0)

            TREE = spatial.KDTree(self.embeddings)
            distances, indices = TREE.query(_mean, k=5)
            indices = indices.tolist()
            movie_names = [self.embeddings.index[ii] for ii in indices]
            movie_names = [ep for ep in movie_names if ep not in [option for title in titles for option in clean_movie_string(title)]]

        return movie_names





    def process_input(self, user_input = None):  # processes user's initial message
        # if user_input is None:
        #     user_input = input('What would you like to watch today?')
            # TODO: strip newlines so it doesn't crash
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
                            You are only designed to process two movies at a time, so if the user mentions more than two movies,
                            tell them you're not capable of this yet.
                            Do not format response, output it in plain text.
                            Redirect off-topic input if there is any.
                        """))
        self.messages.append(HumanMessage(content = user_input))
        response = self.bot.invoke(self.messages)
        self.messages.append(response)
        return response.content
        # try:  # verify that the bot outputs a list. it won't work if the user gives off-topic input
        #     correct_output_type = type(eval(response.content)) == list
        #     print(response)
        #     return eval(response.content)
        # except:
        #     print(response.content)  # if the bot outputs something that's not a list, print its response
        #     return self.process_input()  # then try asking for input again


    # TODO: spit out the recs in plain language
    def give_recs(self, recs):
        self.messages.append(
            SystemMessage("""
                The input message is a Python list of movie titles. 
                You are to recommend these movies in natural language based on their previous query.
                Don't justify the recommendations, just offer them concisely.
                Make sure the movies are properly capitalized in the output, since the input may not be.
                Redirect off-topic input if there is any.
            """))
        self.messages.append(HumanMessage(content = str(recs)))
        response = self.bot.invoke(self.messages)
        self.messages.append(response)
        # print(response.content)
        return response.content
