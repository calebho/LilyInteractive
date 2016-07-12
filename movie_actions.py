import webbrowser
# import win32com.client
import time

# from parsers import parse_choices
from speech_recog import getInputString, getInputStringMultiple
from text_to_speech import speak, wrap_text, englishify

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
    text = "Welcome to the box office. Which movie would you like to watch?"
    text += "We have tickets for "
    text += englishify(movie_names)
    text = wrap_text(text, "GoodNews")
    speak(text)

    inp = getInputString()
    movie_choice = get_choices(inp, movie_names) 
    while len(movie_choice) != 1:
        if not movie_choice:
            speak(wrap_text("Sorry we don't have tickets for that movie.",
                            "Apology"))
        elif len(movie_choice) > 1:
            speak(wrap_text("Please choose only one movie"))
        movie_choice = get_choices(inp, movie_names)
    # while True:
    #     try:
    #         choices = parse_choices(movie_choice, "I'd like to watch Minions")
    #     except RuntimeError:
    #         speak("I'm sorry, I didn't understand that")
    #     if len(choices) == 1:
    #         speak("Please pick one movie to watch")
    #     elif choices[0].lower() in movie_names:
    #         break
    #     else:
    #         speak("Sorry we don't have tickets for %s" % choices[0])

    text = "Here's your ticket. Enjoy the show. "
    text += "Would you like to go to the concessions or the ticket checker?"
    text = wrap_text(text, "GoodNews")
    speak(text)

    return {'movie_choice': movie_choice}

def concessions(menu):
    """Getting snacks. 
    """
    bought = []
    text = "What can I get for you? We have " # what if user says nothing?
    text += englishify(menu)
    text = wrap_text(text, "GoodNews")
    speak(text)

    while True:
        inp = getInputString() # TODO: handle multiple inputs?
        if "no" in inp.lower():
            break
        item_choices = get_choices(inp, menu)
        for item in item_choices:
            if item not in bought:
                bought.append(item)
        speak(wrap_text("Can I get anything else for you?", "GoodNews"))

    text = "Thank you. "
    text += "If you do not have your ticket yet, go to the box office."
    text += "Otherwise, you can go to the ticket checker."
    text = wrap_text(text, "GoodNews")
    speak(text)

    return {'bought': bought}

def ticket_checker(movie_choice):
    """Checks the user's ticket and gives directions to the corresponding
    theater
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

def watch_movie(movie_choice):
    """Plays the movie
    """
    # TODO
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
    movie_greeting('Caleb')

if __name__ == '__main__':
    main()
