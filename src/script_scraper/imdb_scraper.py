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

    
