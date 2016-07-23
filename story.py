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

    def check_context_for(self, node, *args, **kwargs):
        """Add a run condition to `node` that checks whether keys `args` exist
        in the context and whether key-value pairs `kwargs` exist in the
        context
        """
        def check(*args, **kwargs):
            missing = []
            for arg in args:
                if arg not in self._context:
                    missing.append(arg)
            
            wrong_values = []
            for k, v in kwargs.iteritems():
                if k in self._context:
                    match = v == self._context[k]
                    if not match:
                        wrong_values.append((k, v))
                else:
                    missing.append(k)

            if missing or wrong_values:
                # TODO: output something useful
                return False
            else:
                return True

        self.node[node]['run_conditions'].append(check)

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
    
    def verify(self):
        """Does some simple checks to see whether the story is well formed
        """
        self._verify_arg_dict()
        self._check_current()
        # TODO: check for circular dependencies?

    def add_say(self, node, message):
        self._add_action(node, 'say', message=message)

    def add_listen(self, node, intent): # TODO: more parameters probably needed
        self._add_action(node, 'listen', intent=intent)

    def add_play(self, node, filename):
        self._add_action(node, 'listen', filename=filename)

##########################################################################
####################### PRIVATE ##########################################
##########################################################################

    def _add_action(self, node, kind, **kwargs):
        """Add an action of type `kind` to node `node` 

        Parameters:
        node {str} The node the action is added to
        kind {str} The type of action being added
        kwargs {dict} The keyword arguments passed to the methods controlling
                      the actions.
        """
        kind = kind.lower()
        if kind not in ['say', 'listen', 'play']:
            raise StoryError('That is not a valid action')

        action = {'type': kind, 'kwargs': kwargs}
        self.node[node]['actions'].append(action)

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
        """Run the current node
        """
        if self._is_finished or not self._current:
            return 

        for action in self.node[node]['actions']:
            self._do(action)

    def _do(self, action):
        """
        """
        action_type = action['type']
        kwargs = action['kwargs']
        if action_type == 'say':
            self._say(**kwargs)
        elif action_type == 'listen':
            self._listen(**kwargs)
        elif action_type == 'play':
            self._play(**kwargs)

    def _say(self, message):
        """Output message
        """
        self._output_fct(message)

    def _listen(self, intent):
        """Get input and listen for intent
        """
        while True:
            inp = self._input_fct()
            resp = parse(inp, self.workspace_id)
            if get_intent(resp) == intent:
                pass # TODO: what to do here?
            else:
                error_msg = "Sorry, I didn't understand what you said. " +\
                        "Could you try rephrasing?"
                self._output_fct(error_msg)

    def _play(self, filename):
        """Play multimedia
        """
        raise NotImplementedError('TODO')

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
    
