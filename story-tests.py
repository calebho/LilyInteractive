import unittest

from story import Story, StoryNode, StoryError, get_keys, get_value

class StoryTests(unittest.TestCase):

    def setUp(self):
        foo = lambda: None 
        n = StoryNode(foo)
        # self.s = Story('a')

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
