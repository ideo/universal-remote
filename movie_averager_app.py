import dotenv
from movie_averager_app_src import logic as lg
import streamlit as st

st.set_page_config(
    page_title="Movie Averager",
    page_icon="🧪",
    layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

dotenv.load_dotenv()


# I want a movie that's like Finding Nemo but a little more like Rush Hour  # this one puts more weight on rush hour
# I want a movie that's like Finding Nemo but a little bit like Rush Hour
# I want a movie that's like Finding Nemo but a tiny bit like Rush Hour
#
# Give me a cross between Robocop and Marley & Me
# Give me the love child of American Psycho and The Matrix
# Give me the love child of Finding Nemo and Robocop
#
# What if Juno and Clueless had a baby?
#
# back to the future x goonies
# zach: robocop x care bears

_, cntr, _ = st.columns([2,7,2])
with cntr:
    st.title("Movie Averager")
    st.subheader("Tell our chatbot in natural language what two movies you'd like to mash up, and it'll return its best recommendation out of its database of 1000+ movies!")

left, right = st.columns([3,5])

testbot = lg.Bot(advanced = True)
# testbot = lg.Bot(advanced = False)

with left:
    st.header('Movies you can use')
    st.write("You can use your browser's search function to quickly see if a specific movie is in the database. Be sure to spell the movies correctly when using the bot!")
    with st.container(height = 600):
        st.table(testbot.synopses)

with right:
    st.header('Chat with me here')
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
    st.subheader('How this prototype could improve')
    st.write('TBD')


    #     recs_list = testbot.average_embeddings(init_response)
    #     testbot.give_recs(recs_list)

