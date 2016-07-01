from movie_story import movie_story_factory
from story import StoryError

# movie story elements
MOVIE_LIST = ["inside out", "tomorrowland", "minions", "home"]
MENU = ["soda", "popcorn", "candy"]

# zoo story elements
EXHIBITS = ["monkeys", "elephants", "lions", "otters", "pandas", "tigers",
            "penguins"]

def get_name():
    """Gets the user's name
    """
    return raw_input("What's your name? ")

def get_story():
    """Gets a story choice from the user and returns the appropriate Story object
    and player dict
    """
    story_choice = 'movie'
    if story_choice == 'movie':
        s = movie_story_factory()
        player = {'name': get_name(),
                  'movie names': MOVIE_LIST,
                  'menu': MENU,
                  'bought': None,
                  'movie choice': None}
    elif story_choice == 'zoo':
        s = zoo_story_factory()
        player = {'name': get_name(),
                  'exhibits': EXHIBITS,
                  'next': None}
    elif story_choice == 'pet store':
        pass

    return s, player

def main():
    s, player = get_story()

    s.current(player)
    node_dict = s.get_nodes_by_name()
    while not s.is_finished():
        print 'current:', s.current
        next_node = raw_input('Next node? ')
        if next_node.strip() in node_dict:
            try:
                s.current = node_dict[next_node]
                s.current(player)
            except StoryError as e:
                print str(e)
        else:
            print '%s is not a valid node' % next_node


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
