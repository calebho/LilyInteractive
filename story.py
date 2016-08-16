from __future__ import print_function

import networkx as nx
import random
import inspect 
import webbrowser
import warnings

from functools import wraps
from parsers import parse, get_intent, get_entities
from numpy.random import multinomial
from copy import copy 
from text_to_speech import englishify

class StoryError(Exception):
    pass

class Story(nx.DiGraph):
    """The Story class represented as a directed graph.
    """

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

    def get_actions(self, n=None):
        if n:
            return self.node[n]['actions']
        elif self._current:
            return self.node[self._current]['actions']
        else:
            return []

    # TODO: might not be very useful
    def get_run_conditions(self, n=None):
        """Gets the run conditions list of node `n`. If not provided, defaults
        to current. If current is not set, returns an empty list
        """
        if n:
            return self.node[n]['run_conditions']
        elif self._current:
            return self.node[self._current]['run_conditions']
        else:
            return []

    def get_dynamic_events(self, n=None):
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
        node_attributes = {'actions': None,
                           'dynamic_events': None,
                           'run_conditions': None}
        super(Story, self).add_node(str(s), **node_attributes)

    def add_nodes_from(self, nodes):
        """Given a list of nodes, add them to the graph
        """
        nodes = [str(node) for node in nodes]
        node_attributes = {'actions': None,
                           'dynamic_events': None,
                           'run_conditions': None}
        super(Story, self).add_nodes_from(nodes, **node_attributes)
    
    def require_visit(self, u, *nodes):
        """Add a run condition to `u` that requires nodes in `nodes` to be 
        visited beforehand
        """
        def check():
            # print('checking:', u)
            # print('nodes:', nodes)
            unvisited = []
            for node in nodes:
                if node not in self._visited:
                    unvisited.append(node)
            # print('unvisited:', unvisited)
            if unvisited:
                # TODO: output something useful
                return False
            else:
                return True

        if not self.node[u]['run_conditions']:
            self.node[u]['run_conditions'] = []
        self.node[u]['run_conditions'].append(check)

    def check_context_for(self, node, *args, **kwargs):
        """Add a run condition to `node` that checks whether keys `args` exist
        in the context and whether key-value pairs `kwargs` exist in the
        context
        """
        def check():
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

        if not self.node[node]['run_conditions']:
            self.node[node]['run_conditions'] = []
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
        self._check_current()
        # TODO: check for circular dependencies?

    def add_say(self, node, message, only_if=None):
        self._add_action(node, 'say', message=message, only_if=only_if)

    def add_listen(self, node, intent, entity_type='', n_entities=0, 
            verify_with='', context_key='', fail_message='', only_if=None): 
        """Add a listen action to node `node`

        Parameters:
        node {str} The node the action is being added to
        intent {str} The target intent of the message
        entity_type {str} The type of entity to listen to
        n_entities {int} The maximum number of entities to accept. 0 means
                         no limit
        verify_with {str} A key for self.context whose value is a list. Each
                          entity extracted is then tested 
        """
        # assert type(entity_type) is str, 'entity_type is %s' % type(entity_type)
        if context_key not in self._context:
            warnings.warn('%s not in context' % context_key, RuntimeWarning)
        if verify_with not in self._context:
            warnings.warn('%s not in context' % verify_with, RuntimeWarning)
        assert n_entities >= 0
        self._add_action(node, 'listen', intent=intent, entity_type=entity_type, 
                n_entities=n_entities, verify_with=verify_with, 
                context_key=context_key, fail_message=fail_message, only_if=only_if)

    def add_play(self, node, source, only_if=None):
        # TODO: validate source???
        self._add_action(node, 'play', source=source, only_if=only_if)

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
        if not self.node[node]['actions']:
            self.node[node]['actions'] = []
        self.node[node]['actions'].append(action)

    def _check_current(self):
        """Checks that current is set 
        """
        if not self._current:
            raise RuntimeWarning('Current is `None`')

    def _get_next(self):
        """Gets the next node from the user and returns the appropriate node
        """
        if not self._current:
            return
        elif not self.neighbors(self._current): # current is a leaf node
            self._is_finished = True
            return

        while True:
            user_inp = self._input_fct() 
            resp = parse(user_inp, self.workspace_id)
            intent = get_intent(resp)

            if intent in self.neighbors(self._current):
                if self._is_runnable(intent): # will output something when False
                    return self._select(intent)
            elif intent:
                msg = "Sorry I can't go to %s" % user_inp
                self.output_fct(msg)
            else:
                msg = "Sorry I didn't catch that. Could you repeat yourself?"
                self.output_fct(msg)
                    
    def _select(self, node):
        """Selects a node to return based on the probability distrubtion
        given by `dynamic_events`
        """
        dynamic_events = self.get_dynamic_events(node)
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

        if self.node[self._current]['actions']:
            for action in self.node[self._current]['actions']:
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

    def _say(self, message, only_if=None):
        """Output message
        """
        if only_if and not self._check_only_if(*only_if):
            return
        context_copy = self._context.copy()
        for k, v in context_copy.iteritems():
            if type(v) is list and len(v) > 0:
                if type(v[0]) is str:
                    context_copy[k] = englishify(v)
                elif v[0] == 0:
                    context_copy[k] = englishify(v[1:])
                elif v[0] == 1:
                    context_copy[k] = englishify(v[1:], conj=False)
                else:
                    raise StoryError('Unknown option %s' % v[0])
                
        self._output_fct(message.format(**context_copy))

    def _listen(self, intent, entity_type='', n_entities=0, verify_with='', 
            context_key='', fail_message='', only_if=None):
        """Get input and listen for intent
        """
        if only_if and not self._check_only_if(*only_if):
            return
        assert self.workspace_id, 'No valid workspace ID'
        while True:
            # transcribe audio and parse it
            inp = self._input_fct()
            resp = parse(inp, self.workspace_id)
            if get_intent(resp) != intent.strip():
                error_msg = "Sorry, I didn't understand what you said. " +\
                        "Could you try rephrasing?"
                self._output_fct(error_msg)
                continue # mismatching intent so start over
            
            entities = get_entities(resp)
            # chop off entities if necessary
            if n_entities:
                entities = entities[:n_entities]
            # print(entities)
            
            # print('key:', context_key)
            if context_key:
                if verify_with:
                    # print('verifying with:', verify_with)
                    valid_entities = self._context[verify_with]
                    has_invalid_entities = False
                    for entity in entities:
                        if entity not in valid_entities:
                            has_invalid_entities = True
                            break
                    if has_invalid_entities:
                        # print('has invalid entities')
                        default_msg = "I didn't recognize something you said. " +\
                                "Could you repeat yourself?"
                        msg = fail_message if fail_message else default_msg
                        self._output_fct(msg)
                        continue
                if len(entities) == 0:
                    # print('entites has len 0')
                    pass
                elif len(entities) == 1:
                    # print('context updated')
                    self._context[context_key] = entities[0]
                else:
                    # print('context updated')
                    self._context[context_key] = entities
            return # none of the continues were hit

    def _play(self, source, only_if=None):
        """Display media with URL `source`

        Parameters:
        source {str} The URL of the media
        only_if {tuple} A k, v context pair that causes the node to evalute
                        only if self.context[k] == v
        """
        if only_if and not self._check_only_if(*only_if):
            return
        webbrowser.open(source, new=2)

    def _check_only_if(self, k, v):
        if self._context[k] == v:
            return True
        else:
            return False

    def _is_runnable(self, n):
        """Checks whether the run conditions are satisifed for node `n` 
        """
        return self._check_conditions(self.get_run_conditions(n))

    def _check_conditions(self, l):
        """Helper for is_runnable
        """
        if not l:
            return True 
        elif len(l) == 1:
            return l[0]()
        else:
            return l[0]() and self._check_conditions(l[1:])
    
