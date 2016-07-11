import unittest

from story import Story, StoryNode, StoryError, StoryNodeError, get_keys, \
                  get_value

class StoryTests(unittest.TestCase):

    def setUp(self):
        self.s = Story()
        foo = lambda: None 
        start = StoryNode(foo)
        self.s.add_node(start, start=True)

    def tearDown(self):
        del self.s

    def test_add(self):
        with self.assertRaises(AssertionError):
            self.s.add_node('s')
    
        bar = lambda: None 
        with self.assertRaises(StoryError):
            self.s.add_node(bar, start=True)
        self.s.add_node(bar)
        self.assertTrue(bar in self.s)


    # def test_get(self):
    #     with self.assertRaises(AssertionError):
    #         self.s.get_node('not a callable')

    #     with self.assertRaises(StoryError):
    #         foo = lambda: None 
    #         self.s.get_node(foo)

    #     foo = lambda: None 
    #     foo_node = self.s.add_node(foo)
    #     self.assertTrue(self.s.get_node(foo) == foo_node)
    
    def test_context(self):
        d = {'a': 1, 'b': 2}
        self.s.context = d
        self.assertTrue(self.s.context == d)
        d['c'] = 3
        self.assertFalse(self.s.context == d)

    def test_add_edge(self):
        a = 'not callable'
        b = 'also not callable'
        with self.assertRaises(AssertionError):
            self.s.add_edge(a, b)
        
        f1 = lambda: None
        f2 = lambda: None 
        self.s.add_edge(f1, f2)
        self.assertTrue(f1 in self.s)
        self.assertTrue(f2 in self.s)
        self.assertTrue(f2 in self.s.neighbors(f1))
        self.assertFalse(f1 in self.s.neighbors(f2))
        
        g1 = lambda: None 
        g2 = lambda: None 
        h1 = lambda: None 
        h2 = lambda: None 
        ebunch = [(g1, g2), (h1, h2)]
        self.s.add_edges_from(ebunch)
        for fct1, fct2 in ebunch:
            self.assertTrue(fct1 in self.s)
            self.assertTrue(fct2 in self.s)
            self.assertTrue(fct2 in self.s.neighbors(fct1))
            self.assertFalse(fct1 in self.s.neighbors(fct2))

    # def test_add_undir_edge(self):
    #     a = 'not callable'
    #     b = 'also not callable'
    #     with self.assertRaises(AssertionError):
    #         self.s.add_undirected_edge(a, b)
    #     
    #     f1 = lambda: None
    #     f2 = lambda: None 
    #     n2 = StoryNode(f2)
    #     self.s.add_undirected_edge(f1, n2)
    #     n1 = self.s.get_node(f1)
    #     self.assertTrue(n1 in self.s)
    #     self.assertTrue(n2 in self.s)
    #     # print self.s.nodes()
    #     # print self.s.edges()
    #     self.assertTrue(n1 in self.s and n2 in self.s)
    #     self.assertTrue(n2 in self.s.neighbors(n1))
    #     self.assertTrue(n1 in self.s.neighbors(n2))
    #     
    #     g1 = lambda: None 
    #     g2 = lambda: None 
    #     h1 = lambda: None 
    #     h2 = lambda: None 
    #     ebunch = [(g1, g2), (h1, h2)]
    #     self.s.add_undirected_edges_from(ebunch)
    #     for fct1, fct2 in ebunch:
    #         n1 = self.s.get_node(fct1)
    #         n2 = self.s.get_node(fct2)
    #         self.assertTrue(n1 in self.s)
    #         self.assertTrue(n2 in self.s)
    #         self.assertTrue(n2 in self.s.neighbors(n1))
    #         self.assertTrue(n1 in self.s.neighbors(n2))




class StoryNodeTests(unittest.TestCase):
    
    def setUp(self):
        self.a = StoryNode(lambda: None)

    def tearDown(self):
        del self.a

    def test_arg_dict(self):
        self.assertTrue(not self.a.arg_dict) # no arguments 

        with self.assertRaises(AssertionError):
            d = {'arg': 'arg'}
            self.a.arg_dict = d

        b = StoryNode(lambda x: x)
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

        d = {'a': 0.5, 'b': 0.5}
        with self.assertRaises(AssertionError):
            self.a.dynamic_events = d 

        u = StoryNode(lambda: None)
        v = StoryNode(lambda: None)
        d = {u: 1, v: 2}
        with self.assertRaises(AssertionError):
            self.a.dynamic_events = d 

        d[u] = 0.25 
        d[v] = 0.75
        self.a.dynamic_events = d 
        # print self.a.dynamic_events
        self.assertTrue(self.a.dynamic_events == {u: 0.25, v: 0.75})
        d[u] = 0.1 
        d[v] = 0.1
        self.assertTrue(self.a.dynamic_events == {u: 0.25, v: 0.75})
        self.a.dynamic_events = d 
        self.assertTrue(self.a.dynamic_events == {u: 0.1, v: 0.1})

    def test_is_runnable(self):
        self.a.run_conditions = [lambda: True, lambda: True]
        self.assertTrue(self.a.is_runnable())

        self.a.run_conditions = [lambda: False, lambda: True]
        self.assertFalse(self.a.is_runnable())

    def test_select(self):
        self.assertTrue(self.a.select() == self.a)

        b = StoryNode(lambda: None)
        self.a.dynamic_events = {b: 0.5}
        a_flag = False 
        b_flag = False
        for i in range(10):
            if self.a.select() == self.a: a_flag = True
            if self.a.select() == b: b_flag = True
        # unlikely that the same node is chosen 10 times in row
        self.assertTrue(a_flag and b_flag) 


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
