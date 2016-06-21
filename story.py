import networkx as nx

def get_keys(d):
    """Recursively get the keys of a nested dictionary and return them as a set
    """
    to_ret = set()
    for k, v in d.iteritems():
        to_ret.add(k)
        if type(v) is dict:
            to_ret = to_ret | get_keys(v) # union

    return to_ret

def get_value(d, k):
    """Given a nested dict `d` and a key `k`, get the value of d at `k`

    Returns: {dict} If `k` is not a leaf {None} If `k` is a leaf or `k` does not
             exist
    """
    if not d:
        return

    keys = d.keys()
    if k in keys:
        return d[k]
    else:
        for v in d.itervalues():
            to_ret = get_value(v, k)
            if to_ret:
                return to_ret
        return

class StoryError(Exception):
    pass

class StoryNode(object):
    """A story node representing a time period in the story
    """

    def __init__(self, name, activity):
        """StoryNode constructor

        Parameters:
        name {str} The name of the node
        activity {callable} A function representing an activity
        """
        self._name = name
        self._activity = activity

    @property
    def name(self):
        return self._name

    def __call__(self, *args, **kwargs):
        self._activity(*args, **kwargs)

    def __str__(self):
        return self._name

    def __hash__(self):
        return hash(repr(self))

class Story(nx.DiGraph):
    """The Story class represented as a directed graph
    """

    def __init__(self, start, dependencies={}):
        """Constructor for Story

        Parameters:
        start {StoryNode} The starting point of the story
        dependencies {dict} A tree describing StoryNode dependencies. Leaf nodes
                            should have value None
        """
        # TODO: player field?
        super(Story, self).__init__()
        self._current = start
        self._visited = set([start])
        self._dependencies = None
        self.dependencies = dependencies

        super(Story, self).add_node(start)


    @property
    def current(self):
        return self._current

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def visited(self):
        return self._visited

    @current.setter
    def current(self, node):
        if node in self.neighbors(self._current):
            unmet_deps = self._check_deps(node)
            if unmet_deps:
                s = "[%s] has unmet dependencies: " % str(node)
                for dep in unmet_deps:
                    s += "[%s] " % str(dep)
                raise StoryError(s)
            else:
                self._current = node
                self._visited.add(node)
        else:
            raise StoryError("%s is not a neighbor of %s" % \
                             (str(node), str(self._current)))

    @dependencies.setter
    def dependencies(self, d):
        """Sets the dependencies attribute. Adds nodes to the graph if necessary
        """
        nodes = get_keys(d)
        for node in nodes:
            if not super(Story, self).has_node(node):
                super(Story, self).add_node(node)

        self._dependencies = d

    def _check_deps(self, node):
        """Check whether StoryNode `node` has any dependencies

        Returns: {list} The list of unmet dependencies
        """
        unmet_deps = []
        v = get_value(self._dependencies, node)
        if v:
            deps = get_keys(v)
            for dep in deps:
                if dep not in self._visited:
                    unmet_deps.append(dep)
            return unmet_deps
        else:
            return []

    def remove_node(self, n):
        if self._current == n:
            raise StoryError('Cannot remove current node')
        super(Story, self).remove_node(n)

    def add_undirected_edge(self, u, v, *args, **kwargs):
        super(Story, self).add_edge(u, v, *args, **kwargs)
        super(Story, self).add_edge(v, u, *args, **kwargs)

    def add_undirected_edges_from(self, ebunch, *args, **kwargs):
        super(Story, self).add_edges_from(ebunch, *args, **kwargs)

        ebunch_reversed = []
        for edge in ebunch:
            new_e = list(edge[:2])
            new_e.reverse()
            if len(edge) == 3:
                new_e.append(edge[2])
            ebunch_reversed.append(tuple(new_e))
        super(Story, self).add_edges_from(ebunch_reversed, *args, **kwargs)

    def is_finished(self):
        """Check whether the story is finished (current is a leaf node)
        """
        return not super(Story, self).neighbors(self._current)

'''
from story_node import StoryNode
from player import Player
#import ctypes
#import time
#lib = ctypes.CDLL('FakeInputWin')
from speech_recog import *
from text_to_speech import *
from nltk.stem.snowball import SnowballStemmer

"""This class represents a story which is built from StoryNodes
and a Player. Given a list of nodes, with the first being the starting node
in the story, it is able to walk between nodes. When a node is visited it
is added as a string in the dictionary of the player. Additionally, any tokens
that are prerequisites for later nodes are added. For example, a box office
node, when visited, will add a 'ticket' to the completed dictionary in player"""

stemmer = SnowballStemmer('english')

class Story(object):
    # set up player and story
    def __init__(self, a_player, the_nodes):
        self.player = a_player
        self.nodes = the_nodes
    # returns child node given by players response, s, if s is a child of the current node
    # otherwise the current node is returned because s is not a valid choice
    def getNextNode(self, current, s):
        #check if user says exactly the node's name
        for child in current.children:
            if s.lower() == child.name.lower():
                return child

        #checks if user says node's name in a longer sentence (node's name can be multiple words)
        stems = []                          #get root of every word to compare
        for word in s.lower().split():
            stems.append(stemmer.stem(word))

        if "quit" in s:
            return None

        for c in current.children_stems:     #for every child of current
            count = 0
            for stem in c:                #for every word in current.child's name
                if stem in stems:         #if the user said that word
                    count += 1          #success, look for next word in name, if applicable
                                        #otherwise, check next child
            if count == len(c):         #if the user said every word in current.child's name
                return current.children[current.children_stems.index(c)]
        return current

    def prereqsValid(self, player, newCurrent):
        for prereq in newCurrent.prereqs:
            if not prereq in player.completed.keys() or player.completed[prereq] == False:
                speak("You do not have your " + prereq + " yet! Choose somewhere else to go.")
                return False
        return True

    # moves the player to the next node in the story based on getNextNode
    def nextNode(self, player):
	# sets current working node to the players present position
        current = player.location

	# automated greeting for node
	# TODO develop better automated 'welcome'
        #speak("Welcome to the " + current.name)

	# a node can have multiple activities associated with it
	# each activity must be completed before moving to next node
        s = current.activity.doActivity(player)


	# prompts user to choose next node out of options
        #speak("You are at the " + current.name + ". Where would you like to go now?")
        #self.printChildren(current)

	#if activity method did not return the next node, then get user's choice
        if s == None:
            s = getInputString()
	# check if a valid choice has been made or if getNextNode has returned the current working node
        newCurrent = self.getNextNode(current, s)
        while (not newCurrent == None) and (newCurrent == current or (not self.prereqsValid(player, newCurrent))):
            if newCurrent == current:
                speak("Sorry, that confused me. Please say one of the following:")
                for c in current.children:
                    speak(c.name)
            s = getInputString()
            newCurrent = self.getNextNode(current, s)
        #once a valid choice is made set current node then return it

        return newCurrent


    def walk(self, player):                         # function to 'play' the story
        while player.location != None:              # while there are still nodes to visit, visit them using nextNode
            player.location = self.nextNode(player)

    def printChildren(self, current):
        for index,child in enumerate(current.children):
            speak(child.name)
'''
