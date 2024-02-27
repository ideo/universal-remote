import dotenv
from movie_averager_app_src import logic as lg
import streamlit

dotenv.load_dotenv()

"""
I want a movie that's like Finding Nemo but a little more like Rush Hour  # this one puts more weight on rush hour
I want a movie that's like Finding Nemo but a little bit like Rush Hour
I want a movie that's like Finding Nemo but a tiny bit like Rush Hour

Give me a cross between Robocop and Marley & Me
Give me the love child of American Psycho and The Matrix
Give me the love child of Finding Nemo and Robocop

What if Juno and Clueless had a baby?

back to the future x goonies
zach: robocop x care bears
"""


testbot = lg.Bot(advanced = True)
# testbot = lg.Bot(advanced = False)
while True:
    init_response = testbot.process_input()
    recs_list = testbot.average_embeddings(init_response)
    testbot.give_recs(recs_list)
