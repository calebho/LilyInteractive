import networkx as nx
import random

from copy import copy

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

    def __init__(self, name, action):
        """StoryNode constructor

        Parameters:
        name {str} The name of the node. Should be unique
        action {callable} A function representing an action
        """
        self._name = name
        self._action = action

    @property
    def name(self):
        return self._name

    def __call__(self, *args, **kwargs):
        return self._action(*args, **kwargs)

    def __str__(self):
        return self._name

    def __hash__(self):
        return hash(self._name)

class Story(nx.DiGraph):
    """The Story class represented as a directed graph
    """

    def __init__(self, start, dependencies={}, random_events={}):
        """Constructor for Story

        Parameters:
        start {hashable} The starting point of the story
        dependencies {dict} A tree describing StoryNode dependencies. Leaf nodes
                            should have value None
        random_events {dict} A dict of `node: list` describing random events
                             that can occur at the specified nodes. The list
                             contains tuples of the form (n, p) where `n` is the
                             "random event" node occuring with probability `p`.
        """
        # TODO: player field?
        super(Story, self).__init__()
        self._current = start
        self._visited = set([start])
        self._dependencies = None
        self.dependencies = dependencies
        self._random_events = None
        self.random_events = random_events

        super(Story, self).add_node(start)


    @property
    def current(self):
        return self._current

    @property
    def dependencies(self):
        return copy(self._dependencies)

    @property
    def random_events(self):
        return copy(self._random_events)

    @property
    def visited(self):
        return copy(self._visited)

    @current.setter
    def current(self, node):
        if node in self.neighbors(self._current):
            if self._check_random(self._current):
                pass # current will be set in check_random
            else:
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

        Parameters:
        d {dict} A nested dictionary representing the dependency tree
        """
        d = copy(d) # copy the dict, but keep existing references
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

    @random_events.setter
    def random_events(self, d):
        """Sets the random_events attribute. Adds nodes to the graph if
        necessary
        """
        # check that the probabilities are valid
        for node in d:
            if d[node]: # handle empty list
                sum_ = sum([p for _, p in d[node]])
                if sum_ > 1:
                    msg = 'Invalid random_events dict; '
                    msg += 'probabilities sum to more than 1'
                    raise StoryError(msg)
            else:
                d[node] = [(None, 0)]

        d = copy(d) # copy the dict, but keep existing references
        for l in d.itervalues():
            for node, _ in l:
                if not super(Story, self).has_node(node):
                    super(Story, self).add_node(node)

        self._random_events = d

    def _check_random(self, node):
        """Given a node `node`, check whether it has a random event associated
        with it. If so, roll to see whether the random event is executed.
        Otherwise, do nothing.  If the random event occurs, set current to the
        node associated with the random event.

        Returns: {bool} True if random event occured, False otherwise 
        """
        if node in self._random_events:
            rand_x = random.random()
            cumulative_p = 0.0
            for next_node, p in self._random_events[node]:
                cumulative_p += p
                if rand_x < cumulative_p:
                    self._current = next_node
                    self._visited.add(next_node)
                    return True
            return False
        else:
            return False

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

    def get_nodes_by_name(self):
        """Returns a dict mapping the names of the nodes to the nodes
        """
        try:
            return {node.name: node for node in super(Story, self).nodes()}
        except AttributeError:
            raise StoryError('One or more nodes is not of type StoryNode')

    def is_finished(self):
        """Check whether the story is finished (current is a leaf node)
        """
        return not super(Story, self).neighbors(self._current)
