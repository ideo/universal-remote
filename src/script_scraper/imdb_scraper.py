from imdb import Cinemagoer, IMDbDataAccessError


IMDB = Cinemagoer()

def get_synopsis(movie_title):
    responses = IMDB.search_movie(movie_title)
    first_hit = responses[0]

    try:
        details = IMDB.get_movie(first_hit.getID())
        plot_outline = details["plot outline"]
        print(f"{first_hit} ✓")
        return plot_outline

    except (KeyError, IMDbDataAccessError, TimeoutError):
        return ""

def get_long_synopsis(movie_title):
    try:
        responses = IMDB.search_movie(movie_title)
        first_hit = responses[0]

        details = IMDB.get_movie(first_hit.getID())
        if 'plot' in details.keys():
            plot_options = details['plot'] + [details['plot outline']]
            plot_lengths = [len(p.split(' ')) for p in plot_options]
            longest_plot = [p for p in plot_options if len(p.split(' ')) == max(plot_lengths)]
            longest_plot = longest_plot[0]
            # longest_plot = longest_plot.split('—')[0:-1]  # strip the username / email (grab everything before the last long dash):
            print(f"{first_hit} ✓")
            return longest_plot
        else:
            plot_outline = details["plot outline"]
            print(f"{first_hit} ✓")
            return plot_outline

    except (KeyError, IMDbDataAccessError, TimeoutError):
        return ""

    
