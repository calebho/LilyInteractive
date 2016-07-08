import networkx as nx
import random
import inspect 

from numpy.random import multinomial
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

    def __init__(self, story, action, arg_dict=None, run_conditions=None, 
                 dynamic_events=None): 
        """StoryNode constructor

        Parameters:
        story {Story} The story that this node belongs to 
        action {callable} The action to be executed at this node 
        arg_dict {dict} The arguments to `action` mapped to the keys in
                        `story.context`. Defaults to the identity map 
        run_conditions {list} A list of callables returning truth-values 
        dynamic_events {dict} A dict of StoryNode:float representing the 
                              probability distribution according to which 
                              nodes are selected 
        """
        assert isinstance(story, Story), \
            "Object passed to `story` is not a Story instance"
        self._story = story
        assert hasattr(action, '__call__'), \
            "Object passed to `action` is not callable"
        self._action = action
        self._arg_dict = None
        if arg_dict:
            self.arg_dict = arg_dict
        else:
            args, _, _, _ = inspect.getargspec(action)
            self._arg_dict = {arg: arg for arg in args}
        self._run_conditions = None
        if run_conditions:
            self.run_conditions = run_conditions
        else:
            self._run_conditions = []
        self._dynamic_events = None
        if dynamic_events:
            self.dynamic_events = dynamic_events
        else: 
            self._dynamic_events = {self: 1.0}

    @property
    def story(self):
        return self._story 

    @property
    def action(self):
        return self._action

    @property
    def arg_dict(self):
        return copy(self._arg_dict)

    @property 
    def run_conditions(self):
        return copy(self._run_conditions)

    @property 
    def dynamic_events(self):
        return copy(self._dynamic_events)

    @arg_dict.setter
    def arg_dict(self, d):
        valid_args, _, _, _ = inspect.getargspec(self._action)
        for arg in d:
            assert arg in valid_args, \
                "%s is not a valid argument to %s" % (arg, self._action.__name__)
        self._arg_dict = copy(d)

    @run_conditions.setter
    def run_conditions(self, l):
        for condition in l:
            assert hasattr(condition, '__call__'), \
                "%s is not callable" % str(condition)
        self._run_conditions = copy(l)

    @dynamic_events.setter
    def dynamic_events(self, d):
        for node in d:
            assert isinstance(node, StoryNode), \
                "%s is not a StoryNode instance" % str(node)
        sum_ = sum([val for val in d.values()])
        assert sum_ <= 1, "The sum of probabilities cannot exceed 1"

        self._dynamic_events = copy(d)
        self._dynamic_events[self] = 1.0 - sum_

    def __call__(self):
        raise NotImplementedError('TODO')

    def __str__(self):
        return self._action.__name__

    def __hash__(self):
        return hash(self._action)

    def select(self):
        """Selects a node to return based on the probability distrubtion
        given by `dynamic_events`
        """
        if self.dynamic_events:
            d_items = zip(*self._dynamic_events.items())
            nodes = d_items[0]
            p_dist = d_items[1]
            sample = list(multinomial(1, p_dist))

            return nodes[sample.index(1)]
        else:
            return self 

class Story(nx.DiGraph):
    """The Story class represented as a directed graph. Nodes connected by
    unweighted edges represent events controlled by the user. For instance 
    if an unweighted edge connects nodes `u` and `v`, the user can freely 
    move from `u` to `v` (or `v` to `u` depending on the direction of the 
    edge). 
    Nodes connected by weighted edges represent events not  controlled by 
    the user (non-player events). For instance, let `u`, `v`, and `w` be 
    nodes in the graph. Let `u` be connected to `v` by a directed edge 
    u --> v with weight `p` and let `u` be connected to `w` by a directed 
    edge u --> w with no weight.
                                 p
                               /---> v 
                             u
                               \---> w
    In this situation, the user can only move to `w`, but there is a chance
    with probability `p` that the user ends up in `v` 
    """

    def __init__(self, start, dependencies=None):
        """Constructor for Story

        Parameters:
        start {hashable} The starting point of the story
        dependencies {dict} A tree describing StoryNode dependencies. Leaf nodes
                            should have value None
        """
        super(Story, self).__init__()
        self._current = start
        self._visited = set([start])
        self._dependencies = None
        if dependencies:
            self.dependencies = dependencies 
        
        super(Story, self).add_node(start)

    @property
    def current(self):
        return self._current

    @property
    def dependencies(self):
        return copy(self._dependencies)

    @property
    def visited(self):
        return copy(self._visited)

    @current.setter
    def current(self, node):
        if node in self.reachables(self._current):
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
            raise StoryError("%s is not reachable from %s" % \
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
            if node not in self:
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
    
    def generate_storyline(self, start):
        """Given a starting node `start`, recursively construct a storyline
        of non-player events by sampling from the probability distribution 
        induced by the outgoing weighted edges 
        """
        if self.neighbors(start) == self.reachables(start):
            # print 'no random events at [%s]' % str(start)
            return []

        possible_nodes = [\
            node for node in self.neighbors(start) if self[start][node]]
        w = lambda dest: self[start][dest]['weight']
        # the weights form a probability distribution w/ indices corresponding
        # to possible nodes  
        weights = [w(dest) for dest in possible_nodes]
        try:
            cumulative_p = sum(weights)
        except ValueError: # one of the weights is `None`
            e_str = 'Weights for outgoing edges from [%s] not all float/int' % str(start)
            raise StoryError(e_str)
        if cumulative_p != 1:
            e_str = 'Weights for outgoing edges from [%s] do not sum to 1' % str(start)
            raise StoryError(e_str)
        sample = list(multinomial(1, weights))
        i = sample.index(1) # find the index of the action chosen 
        next_node = possible_nodes[i]
        if start == next_node: 
            # print 'random event not executed'
            return []
        else:
            # print '[%s] added' % str(next_node)
            return [next_node] + self.generate_storyline(next_node)

    def reachables(self, node):
        """Given a node, return the list of reachable nodes. Reachable nodes
        are defined as nodes that are neighbors of `node` and have an 
        unweighted joining edge 
        """
        edge = lambda dest: self[node][dest] # the edge data 
        return [dest for dest in self.neighbors(node) if not edge(dest)]

    def jump_to(self, node):
        """Jump to a certain point in the story 
        """
        if node in self:
            self._current = node 
        else:
            raise StoryError('%s is not in the story' % str(node))

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