import pandas as pd
# from imdb import Cinemagoer
from src import embedding_utils
import numpy as np
import glob
import os
import re

movie_data = pd.read_csv('data/movie_summaries.csv')
# len(movie_data)

# want to run this on just the movies we haven't already gotten embeddings for
full_pattern = os.path.join(os.getcwd(), 'data/movie_embeddings_instructor*')
filenames = glob.glob(full_pattern)
if filenames != []:  # if there are existing movies with embeddings...
    existing_data = pd.DataFrame()
    for file in filenames:
        existing_data = pd.concat([existing_data, pd.read_csv(file)])

    existing_titles = pd.DataFrame(existing_data[existing_data['dim1'].notna()]['Movie Title'])  # get the movies we already have embeddings for
    existing_titles['embedded'] = True
    movie_data = movie_data.merge(existing_titles, 'left')
    movie_data = movie_data[movie_data['embedded'] != True]

# movie_data = movie_data.iloc[0:3] # testing only

# get embeddings for remaining movies
embedded = embedding_utils.embeddings_dataframe(movie_data, 'instructor')

# get filename for the next file in series
pattern = os.getcwd() + '/data/movie_embeddings_instructor_*'
file_nums = [re.compile(pattern).sub('', filename) for filename in filenames]
file_nums = [re.compile('.csv').sub('', filename) for filename in file_nums]
file_nums = [int(n) for n in file_nums]
next_num = max(file_nums) + 1

# save to csv
filepath = 'data/movie_embeddings_instructor_' + str(next_num) + '.csv'
embedded.to_csv(filepath)

# movie_data_split = np.array_split(movie_data, 10)
# section_index = 1
# for section in movie_data_split:
#     embedded = embedding_utils.embeddings_dataframe(section, 'instructor')
#     filepath = 'data/movie_embeddings_instructor_' + str(section_index) + '.csv'
#     embedded.to_csv(filepath)  # save to csv
#     section_index += 1


