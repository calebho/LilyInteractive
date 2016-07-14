from speech_recog import get_input
from text_to_speech import speak, wrap_text, englishify
import random
# from run_gif import *

yes = ['yes']
yes_syns = [['yes', 'yup', 'yeah', 'yea', 'indeed', 'sure']]

def entrance(name, remaining):
    """Greeting node
    """
    text = "Hi %s. Welcome to the San Diego Zoo! " % name
    text += "We have a bunch of great exhibits for you today. "
    text += "Say the name of the animal you want to see to go there. "
    text += "If you want to leave at any time, just say so. "
    text += "We can go see the " + englishify(remaining, conj=False) + ". "
    text += "Where should we start?"
    text = wrap_text(text, "GoodNews")
    speak(text)

def wallet():
    """Forgot your wallet 
    """
    text = "Oh no! You forgot your wallet! We need to go back and get it. "
    text = wrap_text(text)
    speak(text)

def parking_lot():
    text = "You've reached the parking lot. "
    if random.random() < 0.25:
        text += "Oh no! Some monkeys escaped. "
        text += "They have gotten into your car! "
        # runGif("ZooGifs/monkey_steals_wheel_cover.gif")
        text += "Those thieves got away! "
    text += "We get new exhibits often, so come back soon to see something new. "
    text = wrap_text(text)
    speak(text)

def monkeys(remaining):
    speak(wrap_text("Look at the cute monkeys!", "GoodNews"))
    # runGif("ZooGifs/monkey.gif")
    text = "Where to now? "
    text += update_remaining(remaining, 'monkeys')
    speak(wrap_text(text, "GoodNews"))

def elephants(name, remaining):
    speak("Elephants are my favorite! Check out its cool painting.")
    # runGif("ZooGifs/GIF-Elephant-painting.gif")
    text = "What's next, " + name + "? "
    text += update_remaining(remaining, 'elephants')
    speak(wrap_text(text, "GoodNews"))

def lions(remaining):
    speak(wrap_text("Look, that lion must be hungry.", "GoodNews"))
    # runGif("ZooGifs/lion_tries_to_grab_baby.gif")
    text = "Where would you like to go now? "
    text += update_remaining(remaining, 'lions')
    speak(wrap_text(text, 'GoodNews'))

def penguins(remaining):
    text = "That penguin is a jokester. " # TODO: jokester is mispronounced
    # runGif("ZooGifs/penguin.gif")
    x = random.random()
    if x < 0.75:
        text += "Great timing. They are feeding the penguins. "
        text += "Should we stay and watch? "
        speak(wrap_text(text, 'GoodNews'))
        s = get_input() # TODO: can probably abstract to using story input fct
        # if player.get_target(s, yes, yes_syns) == 'yes':
            # runGif("ZooGifs/penguin_feeding.gif")
        text = "Which animal do you want to see now? "
    else:
        text += "Which animal do you want to see now? "
    text += update_remaining(remaining, 'penguins')
    speak(wrap_text(text, 'GoodNews'))

def tigers(remaining):
    text = "Look at that bird flying into the tiger enclosure. "
    # runGif("ZooGifs/tiger_and_bird.gif")
    x = random.random()
    if x < 0.5:
        text += "There are baby tigers too! "
        text += "Do you want to look? "
        speak(wrap_text(text, 'GoodNews'))
        s = get_input()
        # if player.get_target(s, yes, yes_syns) == 'yes':
            # runGif("ZooGifs/baby_tiger.gif")
        text = "What exhibit should we go to from here? "
    else:
        text += "What exhibit should we go to from here? "
    text += update_remaining(remaining, 'tigers')
    speak(wrap_text(text, 'GoodNews'))

def otters(remaining):
    text = "Check it out - there are otters playing basketball! "
    # runGif("ZooGifs/otter_basketball.gif")
    x = random.random()
    if x < 0.4:
        text += "Look! There is a special great white shark exhibit! "
        text += "Do you want to stop? "
        s = get_input()
        speak(wrap_text(text, 'GoodNews'))
        # if player.get_target(s, yes, yes_syns) == 'yes':
            # runGif("ZooGifs/white_shark_feeding.gif")
        text = "Which animal do you want to see next? "
    else:
        text += "Which animal do you want to see next? "
    text += update_remaining(remaining, 'otters')
    speak(wrap_text(text, 'GoodNews'))

def pandas(name, remaining):
    text = "Look at all of the silly pandas! "
    # runGif("ZooGifs/pandas.gif")
    text += "Where do you want to go now %s? " % name
    text += update_remaining(remaining, 'pandas')
    speak(wrap_text(text, 'GoodNews'))

def update_remaining(l, f_name):
    """Given a list `l` of remaining exhibits and the name `f_name` of the function
    calling this function, update `l` by removing the function whose name is `f_name`
    and return a corresponding prompt
    """
    for i, exhibit in enumerate(l):
        if exhibit == f_name:
            l.pop(i)
    
    if l:
        prompts = ["We haven't seen the %s yet." % englishify(l, conj=False),
                   "We still have to see the %s." % englishify(l)]
    else:
        prompts = ["We've seen everything, but you're welcome to go back to any exhibit"]
    return random.choice(prompts)

