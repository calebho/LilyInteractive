import unittest

from story import Story, StoryError

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

if __name__ == '__main__':
    unittest.main()
