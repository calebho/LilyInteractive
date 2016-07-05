from speech_recog import getInputString
from text_to_speech import speak, wrap_text, englishify
import random
from run_gif import *

yes = ['yes']
yes_syns = [['yes', 'yup', 'yeah', 'yea', 'indeed', 'sure']]

def entrance(p):
    """Greeting node
    """
    text = "Hi %s. Welcome to the San Diego Zoo! " % p['name']
    if random.random() > 0.99:
        text += "Oh no! You forgot your wallet!"
        text = wrap_text(text)
        speak(text)
        return # TODO: perhaps something different for exit

    text += "We have a bunch of great exhibits for you today. "
    text += "Say the name of the animal you want to see to go there. "
    text += "If you want to leave at any time, just say so. "
    text += "We can go see the " + englishify(p['exhibits'], conj=False) + ". "
    text += "Where should we start?"
    text = wrap_text(text, "GoodNews")
    speak(text)

def parking_lot(player):
    text = "You've reached the parking lot. "
    if random.random() > 0.75:
        text += "Oh no! Some monkeys escaped. "
        text += "They have gotten into your car! "
        runGif("ZooGifs/monkey_steals_wheel_cover.gif")
        text += "Those thieves got away! "
    text += "We get new exhibits often, so come back soon to see something new. "

def monkeys(player):
    speak("Look at the cute monkeys!")
    runGif("ZooGifs/monkey.gif")
    speak("Where to now?")
    sayChildren(player)
    return None

def elephantAct(player):
    speak("Elephants are my favorite. Check out its cool painting.")
    runGif("ZooGifs/GIF-Elephant-painting.gif")
    speak("What's next, " + player.name + "?")
    sayChildren(player)
    return None

def lionAct(player):
    speak("Look, that lion must be hungry.")
    runGif("ZooGifs/lion_tries_to_grab_baby.gif")
    speak("Where would you like to go now?")
    sayChildren(player)
    return None

def penguinAct(player):
    speak("That penguin is a jokester.")
    runGif("ZooGifs/penguin.gif")
    x = random.random()
    if x > 0.25:
        speak("Great timing. They are feeding the penguins.")
        speak("Should we stay and watch?")
        s = getInputString()
        if player.get_target(s, yes, yes_syns) == 'yes':
            runGif("ZooGifs/penguin_feeding.gif")
    speak("Which animal do you want to see now?")
    sayChildren(player)
    return None

def tigerAct(player):
    speak("Look at that bird flying into the tiger enclosure.")
    runGif("ZooGifs/tiger_and_bird.gif")
    x = random.random()
    if x > 0.5:
        speak("There are baby tigers too!")
        speak("Do you want to look?")
        s = getInputString()
        if player.get_target(s, yes, yes_syns) == 'yes':
            runGif("ZooGifs/baby_tiger.gif")
    speak("What exhibit should we go to from here?")
    sayChildren(player)
    return None

def otterAct(player):
    speak("Check it out - there are otters playing basketball!")
    runGif("ZooGifs/otter_basketball.gif")
    x = random.random()
    if x > 0.6:
        speak("Look! There is a special great white shark exhibit!")
        speak("Do you want to stop?")
        s = getInputString()
        if player.get_target(s, yes, yes_syns) == 'yes':
            runGif("ZooGifs/white_shark_feeding.gif")
    speak("Which of these animals do you want to see next?")
    sayChildren(player)
    return None

def pandaAct(player):
    speak("Look at all of the silly pandas!")
    runGif("ZooGifs/pandas.gif")
    speak("Where do you want to go now, " + player.name + "?")
    sayChildren(player)
    return None

def sayChildren(player):
    for x in range(0, len(player.location.children) - 1):
        speak(player.location.children[x].name)
