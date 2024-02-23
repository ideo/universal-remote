import dotenv
from movie_averager_app_src import logic as lg

dotenv.load_dotenv()


# embeddings = pd.read_csv('data/movie_embeddings_openai.csv')
synopses, embeddings = lg.load_movie_summary_embeddings()

# testbot = Bot(embeddings)
# init_response = testbot.process_input("I want a movie that's a cross between Finding Nemo and Rush Hour")  # use the godfather to test spelling deviation correction
# print(testbot.average_embeddings(init_response))

"""
I want a movie that's like Finding Nemo but a little more like Rush Hour  # this one puts more weight on rush hour
I want a movie that's like Finding Nemo but a little bit like Rush Hour
I want a movie that's like Finding Nemo but a tiny bit like Rush Hour

Give me a cross between Robocop and Marley & Me
Give me the love child of American Psycho and The Matrix
Give me the love child of Finding Nemo and Robocop

back to the future x goonies
zach: robocop x care bears
"""


testbot = lg.Bot(synopses, embeddings)
while True:
    init_response = testbot.process_input()
    recs_list = testbot.average_embeddings(init_response)
    # print(recs_list)
    print(testbot.give_recs(recs_list))