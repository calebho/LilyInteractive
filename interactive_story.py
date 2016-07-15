from movie_story import movie_story_factory
from zoo_story import zoo_story_factory
from story import StoryError
from speech_recog import get_input
from parsers import parse, get_intent
from text_to_speech import speak, wrap_text

WKSPACE_ID = "34b49656-59ce-4f40-8c32-cc8bb846f8cd"

def get_name():
    """Gets the user's name
    """
    return raw_input("What's your name? ")

def get_story():
    """Gets a story choice from the user and returns the appropriate Story object
    and player dict
    """
    msg = "Where would you like to go today? We can go to the zoo to see " + \
          "some animals, or we can go to the movies and watch a film."
    speak(wrap_text(msg, 'GoodNews'))
    s = None
    while not s:
        inp = get_input()
        resp = parse(inp, WKSPACE_ID)
        intent = get_intent(resp)
        if intent == 'movie':
            s = movie_story_factory()
        elif intent == 'zoo':
            s = zoo_story_factory()
        elif intent == 'pet store':
            pass
        else:
            msg = "I'm sorry, I didn't understand what you said. Could you " + \
                  "try repeating yourself or rephrasing?"
            speak(wrap_text(msg, 'Apology'))

    return s

def main():
    s = get_story()
    s.update_context({'name': get_name()})
    while not s.is_finished:
        s()

main()

