import pandas as pd
import numpy as np
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from sklearn.metrics.pairwise import cosine_similarity
import dotenv
from scipy import spatial

dotenv.load_dotenv()


# just sketching for now!


class Bot:
    def __init__(self, embeddings_df):
        self.bot = ChatOpenAI(model_name='gpt-4-turbo-preview')
        self.embeddings_df = embeddings_df[embeddings_df['dim1'].notna()]
        self.messages = [SystemMessage(content =
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
                        """)]

    def average_embeddings(self, dict_list):  # average two movies and return closest suggestion
        # right now we are assuming that everything is spelled the same way as in the database
        just_embeddings = self.embeddings_df.filter(regex='dim')
        titles = [item['movie'] for item in dict_list]
        rows = [just_embeddings[self.embeddings_df['Movie Title'] == item['movie']] for item in dict_list]
        weights = [item['weight'] for item in dict_list]
        # print(rows)
        # print(weights)
        _mean = np.average(np.array(rows), weights = weights, axis = 0)

        TREE = spatial.KDTree(just_embeddings)
        distances, indices = TREE.query(_mean, k=3)
        indices = indices.tolist()[0]
        episode_names = [embeddings.iloc[ii]['Movie Title'] for ii in indices]
        episode_names = [ep for ep in episode_names if ep not in titles]
        return episode_names




    def process_input(self, user_input = None):  # processes user's initial message
        if user_input is None:
            user_input = input('What would you like to watch today?')
        self.messages.append(HumanMessage(content = user_input))
        response = self.bot.invoke(self.messages)
        print(response)
        return eval(response.content)  # TODO: need to do some spelling deviation correction here. can we use movie titles embeddings / search for this?

    # TODO: spit out the recs in plain language

    # TODO: need chain to put everything together


embeddings = pd.read_csv('data/movie_embeddings_openai.csv')

# testbot = Bot(embeddings)
# init_response = testbot.process_input("I want a movie that's a cross between Finding Nemo and Rush Hour")  # use the godfather to test spelling deviation correction
# print(testbot.average_embeddings(init_response))

# I want a movie that's like Finding Nemo but a little more like Rush Hour  # this one puts more weight on rush hour
# I want a movie that's like Finding Nemo but a little bit like Rush Hour
# I want a movie that's like Finding Nemo but a tiny bit like Rush Hour

# back to the future x goonies
# zach: robocop x care bears

testbot = Bot(embeddings)
while True:
    init_response = testbot.process_input()
    print(testbot.average_embeddings(init_response))