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

    def test_add_edge(self):
        self.s.add_node('a')
        self.s.add_node('b')
        self.s.add_edge('a', 'b')
        self.assertTrue('a' in self.s)
        self.assertTrue('b' in self.s)
        self.assertTrue('b' in self.s.neighbors('a'))
        self.assertFalse('a' in self.s.neighbors('b'))

        self.s.add_edge('c', 'd')
        self.assertTrue('c' in self.s)
        self.assertTrue('d' in self.s)
        self.assertTrue('d' in self.s.neighbors('c'))
        self.assertFalse('c' in self.s.neighbors('d'))

        ebunch = [('b', 'c'), ('d', 'e')]
        self.s.add_edges_from(ebunch)
        self.assertTrue('e' in self.s)
        
    def test_add_undir_edge(self):
        self.s.add_node('a')
        self.s.add_node('b')
        self.s.add_undirected_edge('a', 'b')
        self.assertTrue('a' in self.s)
        self.assertTrue('b' in self.s)
        self.assertTrue('b' in self.s.neighbors('a'))
        self.assertTrue('a' in self.s.neighbors('b'))

        self.s.add_undirected_edge('c', 'd')
        self.assertTrue('c' in self.s)
        self.assertTrue('d' in self.s)
        self.assertTrue('d' in self.s.neighbors('c'))
        self.assertTrue('c' in self.s.neighbors('d'))

        ebunch = [('b', 'c'), ('d', 'e')]
        self.s.add_undirected_edges_from(ebunch)
        self.assertTrue('e' in self.s)

    def test_set_current(self):
        with self.assertRaises(StoryError):
            self.s.current = 'a'
        self.s.add_node('a')
        self.s.current = 'a'
        self.assertTrue('a' in self.s.visited)
        self.assertTrue(self.s.current == 'a')

    def test_add_actions(self):
        self.s.add_node('a')
        s1 = 'This is a test message'
        self.s.add_say('a', message=s1)
        s2 = 'Fake message'
        self.s.add_say('a', message=s2)
        actions = self.s.node['a']['actions']
        self.assertTrue(actions == [{'type': 'say', 'kwargs': {'message': s1}},
                                    {'type': 'say', 'kwargs': {'message': s2}}])

    def test_run_conditions1(self):
        l = ['a', 'b', 'c']
        self.s.add_nodes_from(l)
        
        self.s.require_visit('b', 'a')
        self.s.require_visit('c', 'a', 'b')

        self.assertFalse('a' in self.s.visited)
        condition = self.s.run_conditions('b')[0]
        self.assertFalse(condition())
        condition = self.s.run_conditions('c')[0]
        self.assertFalse(condition())

        self.s.current = 'a'
        condition = self.s.run_conditions('b')[0]
        self.assertTrue(condition())
        condition = self.s.run_conditions('c')[0]
        self.assertFalse(condition())

        self.s.current = 'b'
        condition = self.s.run_conditions('c')[0]
        self.assertTrue(condition())

    def test_run_conditions2(self):
        l = ['a', 'b', 'c', 'd']
        self.s.add_nodes_from(l)
        self.s.context = {'apples': 5}

        self.s.check_context_for('b', 'apples')
        self.s.check_context_for('c', apples=6)
        self.s.check_context_for('d', 'oranges')

        condition = self.s.run_conditions('b')[0]
        self.assertTrue(condition())
        condition = self.s.run_conditions('c')[0]
        self.assertFalse(condition())
        condition = self.s.run_conditions('d')[0]
        self.assertFalse(condition())
        
        updated_context = {'apples': 6, 'oranges': 0}
        self.s.update_context(updated_context)

        condition = self.s.run_conditions('b')[0]
        self.assertTrue(condition())
        condition = self.s.run_conditions('c')[0]
        self.assertTrue(condition())
        condition = self.s.run_conditions('d')[0]
        self.assertTrue(condition())

    def test_context(self):
        d = {'a': 1, 'b': 2}
        self.s.context = d
        self.assertTrue(self.s.context == d)
        self.assertFalse(self.s.context is d)

    '''
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
