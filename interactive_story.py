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


"""
from story import Story
from story_node import StoryNode
from player import Player
from activity import Activity
from theater_acts import *
from zoo_acts import *
from pet_acts import *
from _vault_acts import *
from text_to_speech import *
from speech_recog import *
import movie_story
import zoo_story
import pet_story
import _vault_story
import threading
import avatar_player
import time

#all story titles must be one word

story_dict = {}
story_dict["Movie"] = movie_story.movie_story_line
story_dict["Zoo"] = zoo_story.zoo_story_line
story_dict["Pet"] = pet_story.pet_story_line
#story_dict["Vault"] = _vault_story.vault_story_line

targets_syn = []
for name in story_dict.keys():
    targets_syn.append(stemmer.stem(name))


def getStory():
    speak("Which story would you like to play?")
    for story in story_dict.keys():
        speak(story)
    while True:
        s = getInputStringMultiple()
        story = get_target(s, story_dict.keys(), targets_syn)
        while story == None:
            speak("Sorry, we don't have that story right now.")
            speak("Please try another.")
            for story in story_dict.keys():
                speak(story)
            s = getInputStringMultiple()
            story = get_target(s, story_dict.keys(), targets_syn)
        if story == "quit":
            return None
        return story_dict[story]

def get_target(s, targets, targets_syn):        #this method looks for a one word target in user's speech
    #check if user says exactly the node's name
    if "quit" in s.lower().split():
        return "quit"
    for t in targets:
        if s.lower() == t.lower():
            return t

    s = s.lower().split()
    temp = []
    for i in s:
        temp.append(stemmer.stem(i))
    s = temp
    for t in targets_syn:
        for word in s:
            if word == t:
                return targets[targets_syn.index(t)]

    return None


def runStory():
    #play avatar
    t = threading.Thread(target = avatar_player.run_avatar)
    t.daemon = True
    t.start()
    time.sleep(2)
    #create story from nodes and player
    story_line = getStory()
    if story_line == None:
        return
    player = Player(story_line)
    story = Story(player, story_line)
    #run through the story
    story.walk(player)


runStory()
"""
