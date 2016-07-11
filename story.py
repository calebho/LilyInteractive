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

class StoryNodeError(Exception):
    pass

class StoryNode(object):
    """A story node representing a time period in the story
    """

    def __init__(self, action, story=None, arg_dict=None, run_conditions=None, 
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
        self._story = None
        if story:
            self.story = story

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
        self.run_conditions = run_conditions if run_conditions else []
        
        self._dynamic_events = None
        self.dynamic_events = dynamic_events if dynamic_events else {}

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

    @story.setter
    def story(self, s):
        assert isinstance(s, Story), \
            "Object passed to `story` is not a Story instance"
        self._story = s 

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

    def __call__(self, force=False):
        if force or self.is_runnable():
            c = self._story.context 
            kwargs = \
                {arg_name: c[c_key] for arg_name, c_key in self._arg_dict.items()}
            ret_val = self._action(**kwargs)
            if ret_val:
                self._story.update_context(ret_val)
        else:
            raise StoryNodeError('Run conditions not satisfied')

    def __str__(self):
        return self._action.__name__

    def __hash__(self):
        return hash(self._action)

    def is_runnable(self):
        """Checks run conditions 
        
        Returns: {bool} True if the conditions are satisfied, False otherwise
        """
        return self._check_conditions(self._run_conditions)

    def _check_conditions(self, l):
        """Helper for is_runnable
        """
        if not l:
            return True 
        elif len(l) == 1:
            return l[0]()
        else:
            return l[0]() and self._check_conditions(l[1:])

    def select(self):
        """Selects a node to return based on the probability distrubtion
        given by `dynamic_events`
        """
        if self._dynamic_events:
            d_items = zip(*self._dynamic_events.items())
            nodes = list(d_items[0])
            p_dist = list(d_items[1])
            # add self to occupy leftover probability 
            if sum(p_dist) < 1:
                nodes.append(self)
                p_dist.append(1. - sum(p_dist))
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

    def __init__(self, input_fct=None, output_fct=None):
        """Constructor for Story

        Parameters:
        input_fct {callable} A callable that accepts some sort of user input 
                             and returns a str 
        output_fct {callable} A callable that accepts a str and produces some
                              sort of output 
        """
        super(Story, self).__init__()
        # self._node_dict = {} # maps callable to StoryNode
        # self.add_node(start)
        self._current = None
        self._visited = set()
        self._context = {}
        self._input_fct = None 
        self.input_fct = input_fct 
        self._output_fct = None 
        self.output_fct = output_fct
        # if dependencies:
        #     self.add_dependencies_from(dependencies) # TODO: keep track?

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

    @current.setter
    def current(self, node):
        """
        """
        if node in self:
            self._current = node
        else:
            raise StoryError('%s not in the story' % str(node))

    @context.setter
    def context(self, d):
        self._context = copy(d)

    def update_context(self, d):
        """
        """
        for k, v in d.iteritems():
            self._context[k] = v

    @input_fct.setter
    def input_fct(self, f):
        self._input_fct = f

    @output_fct.setter
    def output_fct(self, f):
        self._output_fct = f

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
        if start and not self._current:
            self._current = c
            self._visited.add(c)
        elif start:
            raise StoryError('Start is already set')
        super(Story, self).add_node(c, arg_dict=arg_dict, 
                                    run_conditions=run_conditions, 
                                    dynamic_events=dynamic_events)
        
    def get_node(self, c):
        """Get a node by its callable
        """
        assert hasattr(c, '__call__'), '%s is not a callable' % str(c)
        if c in self._node_dict:
            return self._node_dict[c]
        else:
            raise StoryError('No StoryNode associated with that callable')

    def get_next(self):
        """
        """
        raise NotImplementedError('TODO')
    
    def run(self):
        """
        """
        raise NotImplementedError('TODO')
    
    def add_dependency(self, u, v):
        """
        """ 
        raise NotImplementedError('TODO')

    def add_dependencies_from(self, d):
        """
        """
        raise NotImplementedError('TODO')

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
