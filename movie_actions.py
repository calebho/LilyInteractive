import webbrowser
import win32com.client
import time

from parsers import parse_choices
from speech_recog import getInputString, getInputStringMultiple
from text_to_speech import speak

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

    Parameters:
    name {str} The name of the user
    """
    speak("Hello! Welcome to the Lehigh Valley Movie Theater")
    speak("You can go to the box office and get your ticket")
    speak("Or you can go to the concessions for some snacks.")
    speak("Where would you like to go, " + name + "?")

def box_office(movie_names):
    """Movie selection

    Parameters:
    movie_names {list} A list of strings containing the available movies

    Returns: {str} The name of the chosen movie
    """
    speak("Welcome to the box office")
    speak("Which movie would you like to watch?")
    for movie_name in movie_names:
        speak(movie_name)
    inp = getInputString()
    movie_choice = get_choices(inp, movie_names)
    while len(movie_choice) != 1:
        if not movie_choice:
            speak("Sorry we don't have tickets for that movie")
        elif len(movie_choice) > 1:
            speak("Please choose only one movie")
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
    speak("Here's your ticket. Enjoy the show.")
    speak("Would you like to go to the concessions?")
    speak("Or would you like to go to the ticket checker?")

    return movie_choice

def concessions(menu):
    """Getting snacks

    Parameters:
    menu {list} A list of strings representing the available snacks

    Returns: {list} The snacks bought
    """
    bought = []
    speak("What can I get for you?") # what if user says nothing?
    speak("We have")
    for item in menu:
        speak(item)
    while True:
        inp = getInputString() # TODO: handle multiple inputs?
        if "no" in inp.lower():
            break
        item_choices = get_choices(inp, menu)
        for item in item_choices:
            if item not in bought:
                bought.append(item)
        speak("Can I get anything else for you?")
    speak("Thank you.")
    speak("If you do not have your ticket yet, go to the box office")
    speak("Otherwise you can go to the ticket checker.")
    speak("Next please!")

    return bought

def ticket_checker(movie_name):
    """Checks the user's ticket and gives directions to the corresponding
    theater
    """
    speak("Hello, ticket please.")
    if movie_name == "inside out":
        speak("Inside Out is in theater 3 A, enjoy the show!")
    if movie_name == "tomorrowland":
        speak("Tomorrowland is in theater 1 D, enjoy your movie!")
    if movie_name == "minions":
        speak("Minions is in theater 3 B, enjoy the show!")
    if movie_name == "home":
        speak("Home is in theater 1 A, enjoy your movie!")
    speak("Say movie to sit down and watch.")

def watch_movie(movie_name):
    """Plays the movie
    """
    speak("Please power off your cellular devices.")
    speak("Sit back, relax and enjoy the show.")
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
