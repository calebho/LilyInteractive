import webbrowser
# import win32com.client
import time

# from parsers import parse_choices
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

def wrap_text(s, t=None):
    """Wrap a string `s` with speak and express-as tags using type `t`
    """
    if t:
        return u"<speak><express-as type=\"%s\">" % t + \
               unicode(s) + \
               u"</express-as></speak>"
    else:
       return u"<speak>" + unicode(s) + u"</speak>"

def movie_greeting(p):
    """The greeting to the movie theater

    Parameters:
    p {dict} The player dict
    """
    text = "Hello! Welcome to the Lehigh Valley Movie Theater. "
    text += "You can go to the box office and get your ticket "
    text += "or you can go to the concessions for some snacks. "
    text += "Where would you like to go %s?" % p['name']
    text = wrap_text(text, "GoodNews")
    speak(text)

def box_office(p):
    """Movie selection. Adds the key `movie choice` to `p`

    Parameters:
    p {dict} The player dict
    """
    text = "Welcome to the box office. Which movie would you like to watch?"
    text += "We have tickets for "
    if len(p['movie names']) == 1:
        text += p['movie names'][0]
    elif len(p['movie names']) == 2:
        text += ' and '.join(p['movie names'])
    else:
        movie_names_copy = p['movie names'][:]
        movie_names_copy[-1] = 'and ' + movie_names_copy[-1]
        text += ', '.join(movie_names_copy)
    text = wrap_text(text, "GoodNews")
    speak(text)

    inp = getInputString()
    movie_choice = get_choices(inp, p['movie names'])
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

    p['movie choice'] = movie_choice[0]

def concessions(p):
    """Getting snacks. Adds the key `bought` to `p`

    Parameters:
    """
    menu = p['menu']
    bought = []
    text = "What can I get for you? We have " # what if user says nothing?
    if len(menu) > 2:
        menu_copy = menu[:]
        menu[-1] = 'and ' + menu[-1]
        menu_str = ', '.join(menu_copy)
    elif len(menu) == 2:
        menu_str = ' and '.join(menu)
    else:
        menu_str = menu[0]
    text += menu_str
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

    p['bought'] = bought

def ticket_checker(p):
    """Checks the user's ticket and gives directions to the corresponding
    theater
    """
    movie_name = p['movie choice']
    text = "Hello, ticket please! "
    if movie_name == "inside out":
        text += "Inside Out is in theater 3 A, enjoy the show! "
    if movie_name == "tomorrowland":
        text += "Tomorrowland is in theater 1 D, enjoy your movie! "
    if movie_name == "minions":
        text += "Minions is in theater 3 B, enjoy the show! "
    if movie_name == "home":
        text += "Home is in theater 1 A, enjoy your movie! "
    text = wrap_text(text, "GoodNews")
    speak(text)

def watch_movie(p):
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
