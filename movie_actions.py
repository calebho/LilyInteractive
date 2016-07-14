import webbrowser
# import win32com.client
import time

from parsers import parse, get_entities, get_intent
from speech_recog import getInputString, getInputStringMultiple
from text_to_speech import speak, wrap_text, englishify

WKSPACE_ID = "569456a8-facf-431d-a963-493d905b77ea" 

# TODO: NAIVE!!!
def get_choices(s, valid_choices):
    """
    """
    to_ret = []
    for choice in valid_choices:
        if choice.lower() in s.lower():
            to_ret.append(choice)

    return to_ret

def movie_greeting(name):
    """The greeting to the movie theater
    """
    text = "Hello! Welcome to the Lehigh Valley Movie Theater. "
    text += "You can go to the box office and get your ticket "
    text += "or you can go to the concessions for some snacks. "
    text += "Where would you like to go %s?" % name
    text = wrap_text(text, "GoodNews")
    speak(text)

def box_office(movie_names):
    """Movie selection. 
    """
    movie_names = [movie.lower() for movie in movie_names]
    text = "Welcome to the box office. Which movie would you like to watch? "
    text += "We have tickets for %s" % englishify(movie_names)
    text = wrap_text(text, "GoodNews")
    speak(text)
    
    while True:
        inp = getInputString()
        resp = parse(inp, WKSPACE_ID)
        if get_intent(resp) == 'buy_ticket':
            entities = get_entities(resp)
            movie_choice = entities[0]
            if movie_choice in movie_names:
                break
            else:
                msg = "Sorry, we're not currently showing %s at the moment. "\
                        % movie_choice
                msg += "Please choose another movie to watch."
                speak(wrap_text(msg, "Apology"))
        else:
            e_msg = "Sorry, I didn't understand what you said. Could you try rephrasing?"
            speak(wrap_text(e_msg, "Apology"))

    text = "Here's your ticket. Enjoy the show. "
    text += "Would you like to go to the concessions or the ticket checker?"
    text = wrap_text(text, "GoodNews")
    speak(text)

    return {'movie_choice': movie_choice}

def concessions(menu):
    """Getting snacks. 
    """
    menu = [item.lower() for item in menu]
    bought = []
    text = "What can I get for you? We have " 
    text += englishify(menu)
    text = wrap_text(text, "GoodNews")
    speak(text)

    while True:
        inp = getInputString() 
        resp = parse(inp, WKSPACE_ID)
        intent = get_intent(resp)
        if intent == 'order_food':
            # print('in order_food')
            entities = get_entities(resp)
            missing = []
            available = []
            for item in entities:
                if item not in menu:
                    missing.append(item)
                elif item not in bought:
                    available.append(item)
                    bought.append(item)
            missing_msg = "" 
            if missing:
                missing_msg = "Sorry we don't have %s on our menu. "\
                        % englishify(missing, conj=False)
                missing_msg = wrap_text(msg, 'Apology')
                # print(missing_msg)
            msg = "I'll get some %s for you. " % englishify(available)
            msg += "Can I get you anything else?" 
            speak(missing_msg + wrap_text(msg, 'GoodNews'))
        elif intent == 'done_ordering':
            # print('done ordering')
            break
        else:
            # print('misunderstanding')
            msg = "I'm sorry, I didn't understand what you said. Could you rephrase?"
            speak(wrap_text(msg, 'Apology'))
            
    text = "Thank you. Here's your %s. " % englishify(bought)
    text += "If you do not have your ticket yet, go to the box office."
    text += "Otherwise, you can go to the ticket checker."
    text = wrap_text(text, "GoodNews")
    speak(text)

    return {'bought': bought}

def ticket_checker(movie_choice):
    """Checks the user's ticket and gives directions to the corresponding
    theater
    """
    # MOVED TO WATCH MOVIE
    text = "Hello, ticket please! "
    if movie_choice == "inside out":
        text += "Inside Out is in theater 3 A, enjoy the show! "
    if movie_choice == "tomorrowland":
        text += "Tomorrowland is in theater 1 D, enjoy your movie! "
    if movie_choice == "minions":
        text += "Minions is in theater 3 B, enjoy the show! "
    if movie_choice == "home":
        text += "Home is in theater 1 A, enjoy your movie! "
    text = wrap_text(text, "GoodNews")
    speak(text)

def watch_movie(movie_choice):
    """Plays the movie
    """
    text = "Hello, ticket please! "
    if movie_choice == "inside out":
        text += "Inside Out is in theater 3 A, enjoy the show! "
    if movie_choice == "tomorrowland":
        text += "Tomorrowland is in theater 1 D, enjoy your movie! "
    if movie_choice == "minions":
        text += "Minions is in theater 3 B, enjoy the show! "
    if movie_choice == "home":
        text += "Home is in theater 1 A, enjoy your movie! "
    text = wrap_text(text, "GoodNews")
    speak(text)
    
    # TODO: need to play the movie
    return

    movie_name = p['movie choice']
    text = "Please power off your cellular devices. "
    text += "Sit back, relax, and enjoy the show."
    text = wrap_text(text, "GoodNews")
    speak(text)
    # TODO: platform specific code
    win32com.client.Dispatch("WScript.Shell").SendKeys('{ESC}')
    if movie_name == "inside out":
        webbrowser.open("https://www.youtube.com/watch?v=_MC3XuMvsDI", new=1)
        fullscreen(130)

    if movie_name == "tomorrowland":
        webbrowser.open("https://www.youtube.com/watch?v=1k59gXTWf-A", new=1)
        fullscreen(132)

    if movie_name == "minions":
        webbrowser.open("https://www.youtube.com/watch?v=eisKxhjBnZ0", new=1)
        fullscreen(167)

    if movie_name == "home":
        webbrowser.open("https://www.youtube.com/watch?v=MyqZf8LiWvM", new=1)
        fullscreen(150)

def fullscreen(length):
    time.sleep(10)
    win32com.client.Dispatch("WScript.Shell").SendKeys('f')
    time.sleep(length)
    win32com.client.Dispatch("WScript.Shell").SendKeys('f')
    win32com.client.Dispatch("WScript.Shell").SendKeys('%{F4}',0)
    
def main():
    menu = ['popcorn', 'Soda', 'canDy']
    concessions(menu)

if __name__ == '__main__':
    main()
