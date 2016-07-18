from __future__ import print_function

import networkx as nx
import random
import inspect 

from functools import wraps
from parsers import parse, get_intent
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
    _node_attributes = {'actions': [],
                        'dynamic_events': {},
                        'run_conditions': []}

    def __init__(self, input_fct=None, output_fct=None, workspace_id=None):
        """Constructor for Story

        Parameters:
        input_fct {callable} A callable that accepts some sort of user input 
                             and returns a str 
        output_fct {callable} A callable that accepts a str and produces some
                              sort of output 
        workspace_id {str} The Watson Conversation workspace ID
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
        self._actions = {}

        self.workspace_id = workspace_id
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

    # def arg_dict(self, n=None):
    #     """Gets the arg dict of node `n`. If not provided, defaults to current.
    #     If current is not set, returns an empty dict
    #     """
    #     if n:
    #         return self.node[n]['arg_dict']
    #     elif self._current:
    #         return self.node[self._current]['arg_dict']
    #     else:
    #         return {}

    # TODO: might not be very useful
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

    def add_node(self, s): 
        """Adds a node to the story 

        Parameters:
        s {str} The name of the node
        """
        super(Story, self).add_node(str(s), attr_dict=_node_attributes)

    def add_nodes_from(self, nodes):
        """Given a list of nodes, add them to the graph
        """
        nodes = [str(node) for node in nodes]
        super(Story, self).add_nodes_from(nodes, attr_dict=_node_attributes)
    
    def require_visit(self, u, *nodes):
        """Add a run condition to `u` that requires nodes in `nodes` to be 
        visited beforehand
        """
        unvisited = []
        def check(*nodes):
            for node in nodes:
                if node not in self._visited:
                    unvisited.append(node)
            if unvisited:
                # TODO: output something useful
                return False
            else:
                return True

        self.node[node]['run_conditions'].append(check)

        # def fail_fct():
        #     # TODO: say unvisited nodes
        #     pass

        # self.add_run_condition(u, check, fail_fct)
        

    # def add_dependency(self, u, v):
    #     """Adds a dependency from u to v. That is to say, going to u depends
    #     on v having been visited already
    #     """ 
    #     condition = lambda: v in self._visited
    #     self.run_conditions(u).append(condition)

    # def add_dependencies_from(self, d):
    #     """Add dependencies from a nested dict describing a dependency tree. 
    #     Leaf nodes represent base dependencies upon which nodes at higher levels
    #     depend
    #     """
    #     if not d:
    #         return

    #     for k, v in d.iteritems():
    #         if v:
    #             for sub_k in v:
    #                 self.add_dependency(k, sub_k)

    #     self.add_dependencies_from(v)

    def add_edge(self, u, v, *args, **kwargs):
        """Given nodes u and v, add them to the graph if necessary and add an
        edge between them
        """
        super(Story, self).add_edge(str(u), str(v), *args, **kwargs)

    def add_edges_from(self, ebunch, *args, **kwargs):
        """Given a list of edges `ebunch`, add them to the graph
        """
        for i, edge in enumerate(ebunch):
            edge = list(edge)
            edge[0], edge[1] = str(edge[0]), str(edge[1])
            edge = tuple(edge)
            ebunch[i] = edge

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
    
    # TODO: might be unnecessary 
    def add_run_condition(self, node, condition, fail_func=None):
        """Add a run condition to node `node`

        Parameters:
        node {str} A node in the graph
        condition {callable} A bool function that checks some condition
        fail_func {callable} What to do when `condition` returns False. Should
                             take the same parameters as `condition`
        """
        if node not in self:
            raise StoryError('Node [%s] does not exist' % node)
        if not hasattr(condition, '__call__'):
            raise StoryError('Condition passed is not a callable')
        if fail_func and not hasattr(fail_func, '__call__'):
            raise StoryError('Fail function passed it not a callable')

        def fail_decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                result = f(*args, **kwargs)
                if not result and fail_func: # f returned False
                    fail_func(*args, **kwargs)
                return result
            return wrapper

        condition = fail_decorate(condition)
        self.node[node]['run_conditions'].append(condition)


    def verify(self):
        """Does some simple checks to see whether the story is well formed
        """
        self._verify_arg_dict()
        self._check_current()
        # TODO: check for circular dependencies?

    def add_say(self, node, message=None):
        """Add an action to node `node` that outputs `message`
        """
        action = {'type': 'say', 'kwargs': {'message': message}}
        self.node[node]['actions'].append(action)

    def add_listen(self, node):
        """Add an action to node `node` that asks for user input 
        """
        action = {'type': 'listen', 'kwargs': None}
        self.node[node]['actions'].append(action)

    def add_play(self, node, filename=None):
        """Add an action to node `node` that plays/shows the media file at
        `filename`
        """
        action = {'type': 'play', 'kwargs': {'filename': filename}}
        self.node[node]['actions'].append(action)


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
            user_inp = self._input_fct() # TODO
            if self.workspace_id: # try to get intention from natural language
                resp = parse(user_inp, self.workspace_id)
                # intents that control node movement should match node names
                intent = get_intent(resp) 
            else: # otherwise use direct matching
                intent = user_inp

            if intent in neighbors:
                node = neighbors[intent]
                if self._is_runnable(node):
                    return self._select(node)
                else:
                    # replace underscores w/ spaces
                    intent_str = ' '.join(intent.split('_')) 
                    msg = "You can't go to the %s yet" % intent_str # TODO: THIS SUCKS
                    self.output_fct(msg)
            else:
                msg = "I'm sorry, I don't understand what you mean. Could you rephrase?"
                self.output_fct(msg)
                    
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
    
