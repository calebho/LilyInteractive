import unittest
import mock

from story import Story, StoryError, get_keys, \
                  get_value

class StoryTests(unittest.TestCase):

    def setUp(self):
        self.s = Story()

    def tearDown(self):
        del self.s

    def test_add_node(self):
        self.s.add_node('a')
        self.assertTrue('a' in self.s)

        self.s.add_node(1)
        self.assertFalse(1 in self.s)
        self.assertTrue('1' in self.s)

        l = ['b', 'c', 'd']
        self.s.add_nodes_from(l)
        for c in l:
            self.assertTrue(c in self.s)
        self.assertTrue('a' in self.s)
        self.assertTrue('1' in self.s)

    '''
    def test_context(self):
        d = {'a': 1, 'b': 2}
        self.s.context = d
        self.assertTrue(self.s.context == d)
        d['c'] = 3 # should not change s.context
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

    def test_add_undir_edge(self):
        a = 'not callable'
        b = 'also not callable'
        with self.assertRaises(AssertionError):
            self.s.add_undirected_edge(a, b)
        
        f1 = lambda: None
        f2 = lambda: None 
        self.s.add_undirected_edge(f1, f2)
        self.assertTrue(f1 in self.s)
        self.assertTrue(f2 in self.s)
        self.assertTrue(f1 in self.s and f2 in self.s)
        self.assertTrue(f2 in self.s.neighbors(f1))
        self.assertTrue(f1 in self.s.neighbors(f2))
        
        g1 = lambda: None 
        g2 = lambda: None 
        h1 = lambda: None 
        h2 = lambda: None 
        ebunch = [(g1, g2), (h1, h2)]
        self.s.add_undirected_edges_from(ebunch)
        for fct1, fct2 in ebunch:
            self.assertTrue(fct1 in self.s)
            self.assertTrue(fct2 in self.s)
            self.assertTrue(fct2 in self.s.neighbors(fct1))
            self.assertTrue(fct1 in self.s.neighbors(fct2))


    def test_run(self):
        # test empty
        self.s()
    
        def foo():
            pass
        def bar():
            pass
        def baz():
            pass
        def a():
            pass
        self.s.add_node(foo, start=True)
        self.s.add_node(bar)
        self.s.add_node(baz)
        self.s.add_node(a)
        self.s.add_edge(foo, bar)
        self.s.add_edge(bar, a)
        self.s.add_edge(foo, baz)
        
        inputs = iter(['bar', 'nonsense', 'baz', 'a'])
        self.s.input_fct = lambda _: next(inputs) 
        while not self.s.is_finished:
            self.s()

    def test_dependencies(self):
        def foo():
            pass
        def bar():
            pass
        def baz():
            pass

        for f in [foo, bar, baz]:
            self.s.add_node(f)

        d = {baz: {bar: {foo: None}}}
        self.s.add_dependencies_from(d)
        for condition in self.s.run_conditions(foo):
            self.assertTrue(condition())
        for condition in self.s.run_conditions(bar):
            self.assertFalse(condition())
        for condition in self.s.run_conditions(baz):
            self.assertFalse(condition())

        self.s.current = foo

        for condition in self.s.run_conditions(foo):
            self.assertTrue(condition())
        for condition in self.s.run_conditions(bar):
            self.assertTrue(condition())
        for condition in self.s.run_conditions(baz):
            self.assertFalse(condition())

        self.s.current = bar

        for condition in self.s.run_conditions(foo):
            self.assertTrue(condition())
        for condition in self.s.run_conditions(bar):
            self.assertTrue(condition())
        for condition in self.s.run_conditions(baz):
            self.assertTrue(condition())

    def test_verify(self):
        def foo(name):
            pass
        self.s.add_node(foo)
        self.s.update_context({'incorrect_name_key': 'Bob'})
        with self.assertRaises(RuntimeWarning):
            self.s.verify()
    
        # map the parameter to foo, `name`, to `incorrect_name_key`
        self.s.node[foo]['arg_dict']['name'] = 'incorrect_name_key'
        self.s.verify()
    '''

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
