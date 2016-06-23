from player import Player
from speech_recog import getInputString, getInputStringMultiple
from text_to_speech import speak
import webbrowser
import win32com.client
import time
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer('english')

#activities must return None or the name of the next node or "quit"

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
    movie_choice = getInputString()
    # TODO: validate movie choice
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

    done = False
    speak("What can I get for you?") # what if user says nothing?
    speak("We have")
    for item in menu:
        speak(item)
    while not done:
        item_choice = getInputString() # TODO: handle multiple inputs?
        # TODO: validate item choice; break statement
        bought.append(item_choice)
        speak("Can I get anything else for you?")
    speak("Thank you.")
    speak("If you do not have your ticket yet, go to the box office")
    speak("Otherwise you can go to the ticket checker.")
    speak("Next please!")

    return bought
    '''
    done = False
    speak("What can I get for you?")
    while not done:
        for i in range(len(menu[0])):
            if not menu[0][i].lower() in player.completed.keys():
                speak(str(menu[0][i]))
        menuChoice = getInputString()
        menu_index = inList(menu[0], menuChoice)
        while menu_index == -1:
            speak("Sorry, we don't have that. Pick another.")
            menuChoice = getInputString()
            menu_index = inList(menu[0], menuChoice)
        if "finished" in menuChoice.lower().split():
            done = True
        else:
            player.completed[menu[0][menu_index]] = True
            speak("Can I get anything else for you?")
    speak("Thank you. Next please!")

    speak("If you do not have your ticket yet, go to the box office")
    speak("Otherwise you can go to the ticket checker.")

    return None
    '''

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

#checks if user says a target phrase in a longer sentence (phrase can be multiple words)
def inList(lst, s):
    for x in lst:                   #if you say exactly phrase in list
        if s.lower() == x.lower():
            return lst.index(x)
    if "quit" in s.lower().split():
        return None
    s = s.lower().split()           #check if you said phrase inside a longer sentence
    temp = []
    for i in s:                     #get root word of user input
        temp.append(stemmer.stem(i))
    s = temp
    for l in lst:                   #for every element in the (movie, food)
        count = 0
        words = l.lower().split()
        for w in words:             #for every word in l(movie title, food name)
            w = stemmer.stem(w)     #compare root words, to increase generaltiy
            if w in s:              #if that word is in what you said
                count += 1
        if count == len(words):      #if you said every word in l
            return lst.index(l)
    return -1


def fullscreen(length):
    time.sleep(10)
    win32com.client.Dispatch("WScript.Shell").SendKeys('f')
    time.sleep(length)
    win32com.client.Dispatch("WScript.Shell").SendKeys('f')
    win32com.client.Dispatch("WScript.Shell").SendKeys('%{F4}',0)
