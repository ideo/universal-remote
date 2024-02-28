# import dotenv
import os
from movie_averager_app_src import logic as lg
import streamlit as st

st.set_page_config(
    page_title="Movie Averager",
    page_icon="🧪",
    layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


# I want a movie that's like Finding Nemo but a little more like Rush Hour  # this one puts more weight on rush hour
# I want a movie that's like Finding Nemo but a little bit like Rush Hour
# I want a movie that's like Finding Nemo but a tiny bit like Rush Hour
#
# Give me a cross between Robocop and Marley & Me
# Give me the love child of American Psycho and The Matrix
# Give me the love child of Finding Nemo and Robocop
#
# What if Juno and Clueless had a baby?
# Give me a movie that's like Clueless but a tiny bit like Pearl Harbor
#
# back to the future x goonies
# zach: robocop x care bears

_, cntr, _ = st.columns([2,7,2])
with cntr:
    st.title("Movie Averager")
    st.subheader("Tell our chatbot in natural language what two movies you'd like to mash up, and it'll return its best recommendation out of its database of 1000+ movies!")
    st.write("Some example prompts:")
    st.write('"Give me the love child of Finding Nemo and Rush Hour"')
    st.write(""" "I want a movie that's like Clueless but a little bit like The Truman Show" """ )
left, right = st.columns([3,5])

testbot = lg.Bot(advanced = True)
# testbot = lg.Bot(advanced = False)

with left:
    st.header('Movies you can use')
    st.write("You can use your browser's search function to quickly see if a specific movie is in the database. Be sure to spell the movies correctly when using the bot!")
    with st.container(height = 600):
        st.table(testbot.synopses)

with right:
    st.header('Chat here')
    bot_interface = st.container(height = 600)

    for message in st.session_state.messages:
        with bot_interface.chat_message(message["role"]):
            st.markdown(message["content"])

    if input_text := st.chat_input('What would you like to watch today?'):
        with bot_interface.chat_message('user'):
            st.markdown(input_text)
            st.session_state.messages.append({"role": "user", "content": input_text})
        init_response = testbot.process_input(user_input = input_text)

        try:  # verify that the bot outputs a list
            correct_output_type = type(eval(init_response)) == list
        except:
            correct_output_type = False

        if correct_output_type:  # if the bot successfully produces the movies dict, proceed to compute recs
            print(init_response)
            recs_list = testbot.average_embeddings(eval(init_response))
            natural_language_recs = testbot.give_recs(recs_list)
            with bot_interface.chat_message('assistant'):
                st.markdown(natural_language_recs)
                st.session_state.messages.append({"role": "assistant", "content": natural_language_recs})
        else:  # if not, because the user gives off-topic input, write the bot's "error" message to screen
            with bot_interface.chat_message('assistant'):
                st.markdown(init_response)
                st.session_state.messages.append({"role": "assistant", "content": init_response})

_, cntr, _ = st.columns([2, 7, 2])
with cntr:
    st.subheader('How it works')
    st.write("""
        This prototype was made possible by scraping the longest synopsis we could find on IMDB for each movie, 
        and getting OpenAI's embeddings for each one. Embeddings are essentially a mapping of texts based on semantic 
        similarity (in this case they are mapped in 1500+ dimensional space). Therefore, the bot's ability to compare 
        movies is limited by the level of detail written in the synopses. 
        
        We wanted the bot's recommendations to resemble what a human implies when they ask for the combo of two movies, 
        i.e. they are probably not asking for a perfect mathematical average between the two movie synopses (which 
        often results in recommendations that aren't related to either movie), but rather they want to mash up the most 
        distinctive features of each one. 
        
        The conversational bot itself is powered with GPT--in this case it is relying on our small database of 
        knowledge rather than the encyclopedic knowledge that ChatGPT has access to. When you tell it "I want a movie 
        that's a like A but a little bit like B", the AI is interpreting your wording to decide to how to weight the 
        movies when mashing up their key features.
    """)
    with st.expander("More mathematical details here...", expanded=False):
        st.write("""
            To find movie recommendations with embeddings, we first used a method called Principal 
            Component Analysis (PCA) to reduce the embeddings' 1500+ dimensions into only 10 dimensions that best summarize 
            the many different ways that movies can vary from one another. Though we didn't try to label these dimensions, 
            one could imagine that some of these dimensions roughly mimic features that humans would use to categorize 
            movies, such as the degree of realism, degree of action, degree of romance etc. Then, for each movie in a 
            user's query, we only look at the 2 features where that movie has the largest absolute value (i.e. a feature 
            where that particular movie is more of an outlier), find the point where those key features intersect, and 
            look for recommendations that exist in that space. If the two movies in the user query share any "key 
            features", we take the average between those. If one movie is weighted more heavily than the other, we 
            moderate the combination of the key features in proportion to the weights.
        """)
    st.subheader('How this prototype could improve')
    st.write("""
        If we were to have used the full scripts for each of these movies, the embeddings would account
        for much more detail, and the recommendations would probably be much more accurate. There are other ways we
        could use AI to analyze the scripts and map out the movies in more dimensions—for instance, using AI to 
        identify how many murders are in each movie, or how many characters there are.
        
        Additionally, we would expect the recommendations to be better if our database consisted of more movies. 
        But I guess the quality of recommendations is up to you to decide!
    """)


