import unittest

from story import Story, StoryNode, StoryError, get_keys, get_value

class StoryTests(unittest.TestCase):

    def setUp(self):
        self.s = Story('a')

    def test_current(self):
        self.assertTrue(self.s.current == 'a')

        self.s.add_node('b')
        with self.assertRaises(StoryError):
            self.s.current = 'b'

        self.s.add_edge('a', 'b')
        self.s.current = 'b'
        self.assertTrue(self.s.current == 'b')

    def test_remove(self):
        self.s.add_edge('a', 'b')
        self.s.current = 'b'
        self.s.remove_node('a')
        with self.assertRaises(StoryError):
            self.s.remove_node('b')

    def test_finished(self):
        self.assertTrue(self.s.is_finished())

        self.s.add_edge('a', 'b')
        self.assertFalse(self.s.is_finished())

        self.s.current = 'b'
        self.assertTrue(self.s.is_finished())

    def test_undirected_edges(self):
        self.s.add_undirected_edge('a', 'b')
        self.assertTrue('b' in self.s.neighbors('a'))
        self.assertTrue('a' in self.s.neighbors('b'))

        edges = [('b', 'c'), ('c', 'a')]
        self.s.add_undirected_edges_from(edges)
        nodes = 'abc'
        for i, node in enumerate(list(nodes)):
            other_nodes = nodes[0:i] + nodes[i+1:]
            for other_node in other_nodes:
                self.assertTrue(other_node in self.s.neighbors(node))

    def test_check_dependencies(self):
        d = {'c': {'b': None}}
        t = Story('a', dependencies=d)
        edges = [('a', 'b'), ('b', 'c'), ('a', 'c')]
        t.add_undirected_edges_from(edges)

        with self.assertRaises(StoryError):
            # 'b' not visited yet
            t.current = 'c'
        self.assertTrue(t.current == 'a')

        t.current = 'b'
        t.current = 'c'

    '''
    def test_story_node(self):
        foo = lambda: None
        a = StoryNode('a', foo)
        b = StoryNode('b', foo)
        c = StoryNode('c', foo)

        self.assertTrue(str(a) == 'a')
        self.assertFalse(a())

        t = Story(a)
        t.add_edge(a, b)
        t.add_edge(a, c)
        self.assertTrue(b in t.neighbors(a))
        self.assertTrue(c in t.neighbors(a))
        self.assertFalse(t.neighbors(b))
        self.assertFalse(t.neighbors(c))
    '''

    def test_np_story(self):
        self.s.add_edge('a', 'b')
        self.s.add_edge('a', 'c')
        self.s.add_edge('a', 'z', weight=0.5)
        with self.assertRaises(StoryError):
            self.s.generate_storyline('a')

        self.s.add_edge('a', 'a', weight=0.5)
        self.s.add_edge('z', 'c')
        self.s.generate_storyline('a')
        self.s.add_edge('z', 'b', weight=0.25)
        self.s.add_edge('z', 'z', weight=0.75)
        self.s.generate_storyline('a')
        for node in 'abcz':
            self.assertTrue(node in self.s)

class StoryNodeTests(unittest.TestCase):
    
    def setUp(self):
        self.s = Story('foo')
        self.a = StoryNode(self.s, lambda: None)

    def test_arg_dict(self):
        self.assertTrue(not self.a.arg_dict) # no arguments 

        with self.assertRaises(AssertionError):
            d = {'arg': 'arg'}
            self.a.arg_dict = d

        b = StoryNode(self.s, lambda x: x)
        self.assertTrue(b.arg_dict == {'x': 'x'})
        b.arg_dict = {'x': 'y'} # map the argument `x` to `y` instead 
        self.assertTrue(b.arg_dict == {'x': 'y'})
        with self.assertRaises(AssertionError):
            b.arg_dict = {'z': 'x'}

        d = {'x': 'x'}
        b.arg_dict = d 
        self.assertTrue(b.arg_dict == d)
        d['y'] = 'y'
        self.assertTrue(b.arg_dict != d) # d was originally copied 

    def test_run_conditions(self):
        self.assertTrue(not self.a.run_conditions)
        l = ['not callable']
        with self.assertRaises(AssertionError):
            self.a.run_conditions = l 

        l = [lambda: True]
        self.a.run_conditions = l 
        self.assertTrue(self.a.run_conditions == l)
        l.append(lambda: False)
        self.assertTrue(self.a.run_conditions != l)

    def test_dynamic_events(self):
        d = {'a': 1, 'b': 2}
        with self.assertRaises(AssertionError):
            self.a.dynamic_events = d 

        u = StoryNode(self.s, lambda: None)
        v = StoryNode(self.s, lambda: None)
        d = {u: 1, v: 2}
        with self.assertRaises(AssertionError):
            self.a.dynamic_events = d 

        d[u] = 0.25 
        d[v] = 0.75
        self.a.dynamic_events = d 
        self.assertTrue(self.a.dynamic_events == {u: 0.25, v: 0.75, self.a: 0})
        d[u] = 0.1 
        d[v] = 0.1
        self.assertTrue(self.a.dynamic_events == {u: 0.25, v: 0.75, self.a: 0})
        self.a.dynamic_events = d 
        self.assertTrue(self.a.dynamic_events == {u: 0.1, v: 0.1, self.a: 0.8})


class GetKeysTests(unittest.TestCase):

    def test_empty(self):
        d = {}
        self.assertEqual(set(), get_keys(d))

    def test_simple(self):
        d = dict.fromkeys('abc')
        self.assertEqual(set(['a', 'b', 'c']), get_keys(d))

    def test_nested(self):
        d = {'a': {'b': None, 'c': None}}
        self.assertEqual(set(['a', 'b', 'c']), get_keys(d))

class GetValueTests(unittest.TestCase):

    def test_empty(self):
        d = {}
        self.assertEqual(None, get_value(d, 'a'))

    def test_simple(self):
        d = dict.fromkeys('abc')
        self.assertEqual(None, get_value(d, 'a'))
        self.assertEqual(None, get_value(d, 'd'))

    def test_nested(self):
        d = {'a': dict.fromkeys('bc')}
        self.assertEqual(dict.fromkeys('bc'), get_value(d, 'a'))
        self.assertEqual(None, get_value(d, 'b'))

if __name__ == '__main__':
    unittest.main()
