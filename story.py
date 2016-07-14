from __future__ import print_function

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

class Story(nx.DiGraph):
    """The Story class represented as a directed graph.
    """

    def __init__(self, input_fct=None, output_fct=None):
        """Constructor for Story

        Parameters:
        input_fct {callable} A callable that accepts some sort of user input 
                             and returns a str 
        output_fct {callable} A callable that accepts a str and produces some
                              sort of output 
        """
        super(Story, self).__init__()
        self._current = None
        self._visited = set()
        self._context = {}
        self._input_fct = None 
        self.input_fct = input_fct 
        self._output_fct = None 
        self.output_fct = output_fct
        self._is_finished = False
        # if dependencies:
        #     self.add_dependencies_from(dependencies) # TODO: keep track?

    def __call__(self):
        """Runs one timestep the story
        """
        self._run_current()
        self.current = self._get_next()

    @property
    def current(self):
        return self._current

    @property
    def visited(self):
        return copy(self._visited)

    @property
    def context(self):
        return copy(self._context)

    @property
    def input_fct(self):
        return self._input_fct

    @property
    def output_fct(self):
        return self._output_fct

    @property
    def is_finished(self):
        return self._is_finished

    def arg_dict(self, n=None):
        """Gets the arg dict of node `n`. If not provided, defaults to current.
        If current is not set, returns an empty dict
        """
        if n:
            return self.node[n]['arg_dict']
        elif self._current:
            return self.node[self._current]['arg_dict']
        else:
            return {}

    def run_conditions(self, n=None):
        """Gets the run conditions list of node `n`. If not provided, defaults
        to current. If current is not set, returns an empty list
        """
        if n:
            return self.node[n]['run_conditions']
        elif self._current:
            return self.node[self._current]['run_conditions']
        else:
            return []

    def dynamic_events(self, n=None):
        """Gets the dynamic events dict of node `n`. If not provided, defaults
        to current. If current is not set, return an empty dict
        """
        if n:
            return self.node[n]['dynamic_events']
        elif self._current:
            return self.node[self._current]['dynamic_events']
        else:
            return {}

    @current.setter
    def current(self, node):
        """Sets current to the provided node and adds node to visited
        """
        if not node:
            pass
        elif node in self:
            self._current = node
            self._visited.add(node)
        else:
            raise StoryError('%s not in the story' % str(node))

    @context.setter
    def context(self, d):
        self._context = copy(d)

    def update_context(self, d):
        """Adds the keys and values in dict `d` to the context dict
        """
        for k, v in d.iteritems():
            self._context[k] = v

    @input_fct.setter
    def input_fct(self, f):
        if f:
            self._input_fct = f
        else:
            self._input_fct = raw_input

    @output_fct.setter
    def output_fct(self, f):
        if f:
            self._output_fct = f
        else:
            self._output_fct = print

    def add_node(self, c, arg_dict=None, run_conditions=None, 
                 dynamic_events=None, start=False):
        """Adds a node to the story 

        Parameters:
        c {callable} A callable representing an specific action in the story
        arg_dict {dict} The arguments to `action` mapped to the keys in
                        `story.context`. Defaults to the identity map 
        run_conditions {list} A list of callables returning truth-values 
        dynamic_events {dict} A dict of StoryNode:float representing the 
                              probability distribution according to which 
                              nodes are selected 
        """
        assert hasattr(c, '__call__'), '%s is not callable' % str(c)
        if not arg_dict:
            args, _, _, _ = inspect.getargspec(c)
            arg_dict = {arg: arg for arg in args}
        if not run_conditions: run_conditions = []
        if not dynamic_events: dynamic_events = {}
        super(Story, self).add_node(c, arg_dict=arg_dict, 
                                    run_conditions=run_conditions, 
                                    dynamic_events=dynamic_events)
        if start and not self._current:
            self.current = c
        elif start:
            raise StoryError('Start is already set')

    def add_nodes_from(self, nodes, arg_dict=None, run_conditions=None,
                       dynamic_events=None):
        for node in nodes:
            assert hasattr(node, '__call__'), '%s is not callable' % str(node)

        if not run_conditions: run_conditions = []
        if not dynamic_events: dynamic_events = {}
        super(Story, self).add_nodes_from(nodes, run_conditions=run_conditions,
                dynamic_events=dynamic_events)
        if not arg_dict:
            for node in nodes:
                args, _, _, _ = inspect.getargspec(node)
                self.node[node]['arg_dict'] = {arg: arg for arg in args}


    def add_dependency(self, u, v):
        """Adds a dependency from u to v. That is to say, going to u depends
        on v having been visited already
        """ 
        condition = lambda: v in self._visited
        self.run_conditions(u).append(condition)

    def add_dependencies_from(self, d):
        """Add dependencies from a nested dict describing a dependency tree. 
        Leaf nodes represent base dependencies upon which nodes at higher levels
        depend
        """
        if not d:
            return

        for k, v in d.iteritems():
            if v:
                for sub_k in v:
                    self.add_dependency(k, sub_k)

        self.add_dependencies_from(v)

    def add_edge(self, u, v, *args, **kwargs):
        """If `u` and `v` aren't StoryNodes, convert them first then add the 
        edge 
        """
        assert hasattr(u, '__call__'), '%s is not callable' % str(u)
        assert hasattr(v, '__call__'), '%s is not callable' % str(v)
        super(Story, self).add_edge(u, v, *args, **kwargs)

    def add_edges_from(self, ebunch, *args, **kwargs):
        """Similar to add edge, convert nodes to StoryNodes first 
        """
        for e in ebunch:
            assert hasattr(e[0], '__call__'), '%s is not callable' % str(e[0])
            assert hasattr(e[1], '__call__'), '%s is not callable' % str(e[1])

        super(Story, self).add_edges_from(ebunch, *args, **kwargs)

    def add_undirected_edge(self, u, v, *args, **kwargs):
        self.add_edge(u, v, *args, **kwargs)
        self.add_edge(v, u, *args, **kwargs)

    def add_undirected_edges_from(self, ebunch, *args, **kwargs):
        self.add_edges_from(ebunch, *args, **kwargs)

        ebunch_reversed = []
        for edge in ebunch:
            new_e = list(edge[:2])
            new_e.reverse()
            if len(edge) == 3:
                new_e.append(edge[2])
            ebunch_reversed.append(tuple(new_e))
        self.add_edges_from(ebunch_reversed, *args, **kwargs)

    def verify(self):
        """Does some simple checks to see whether the story is well formed
        """
        self._verify_arg_dict()
        self._check_current()
        # TODO: check for circular dependencies?

##########################################################################
####################### PRIVATE ##########################################
##########################################################################
    
    def _check_current(self):
        """Checks that current is set 
        """
        if not self._current:
            raise RuntimeWarning('Current is `None`')

    def _verify_arg_dict(self):
        """Checks for any key errors in the arg_dict without running the 
        story
        """
        for node in self:
            arg_dict = self.arg_dict(node)
            for arg, c_key in arg_dict.iteritems():
                if c_key not in self._context:
                    raise RuntimeWarning('%s is not a valid context key' % c_key)

    def _get_next(self):
        """Gets the next node from the user and returns the appropriate node
        """
        if not self._current:
            return
        elif not self.neighbors(self._current): # current is a leaf node
            self._is_finished = True
            return

        neighbors = {f.__name__: f for f in self.neighbors(self._current)}
        
        while True:
            user_inp = self._input_fct('Next? ') # TODO
            if user_inp in neighbors:
                node = neighbors[user_inp]
                if self._is_runnable(node):
                    return self._select(node)
                else:
                    self.output_fct('Run conditions for [%s] not met' % node.__name__)
            else:
                self.output_fct('That is not a valid node')
                    
    def _select(self, node):
        """Selects a node to return based on the probability distrubtion
        given by `dynamic_events`
        """
        dynamic_events = self.dynamic_events(node)
        if dynamic_events:
            d_items = zip(*dynamic_events.items())
            nodes = list(d_items[0])
            p_dist = list(d_items[1])
            # add node to occupy leftover probability 
            if sum(p_dist) < 1:
                nodes.append(node)
                p_dist.append(1. - sum(p_dist))
            sample = list(multinomial(1, p_dist))
            
            return nodes[sample.index(1)]
        else:
            return node

    def _run_current(self):
        """
        """
        if self._is_finished or not self._current:
            return 

        c = self._context
        arg_dict = self.arg_dict() 
        kwargs = \
            {arg_name: c[c_key] for arg_name, c_key in arg_dict.iteritems()}
        ret_val = self._current(**kwargs)
        if ret_val:
            self.update_context(ret_val)

    def _is_runnable(self, n):
        """Checks whether the run conditions are satisifed for node `n` 
        """
        return self._check_conditions(self.run_conditions(n))

    def _check_conditions(self, l):
        """Helper for is_runnable
        """
        if not l:
            return True 
        elif len(l) == 1:
            return l[0]()
        else:
            return l[0]() and self._check_conditions(l[1:])
    
