import unittest
from chronos.graph import Edge, KnowledgeGraph, Node

class GraphTests(unittest.TestCase):
    def setUp(self):
        self.g = KnowledgeGraph()
        self.g.add_node(Node("p1", "Person", "N. A. Kozyrev", "historical", ["S022"]))
        self.g.add_node(Node("t1", "Text", "Experimental study of time", "historical", ["S022"]))

    def test_add_valid_documented_edge(self):
        self.g.add_edge(Edge("p1", "t1", "AUTHORED", "historical", ["S022"]))
        self.assertEqual(len(self.g.edges), 1)

    def test_documented_edge_requires_source(self):
        with self.assertRaises(ValueError):
            self.g.add_edge(Edge("p1", "t1", "AUTHORED", "historical", []))

    def test_edge_requires_existing_nodes(self):
        with self.assertRaises(ValueError):
            self.g.add_edge(Edge("p1", "missing", "RELATED_TO", "hypothesis"))

    def test_duplicate_node_rejected(self):
        with self.assertRaises(ValueError):
            self.g.add_node(Node("p1", "Person", "Duplicate", "historical"))

if __name__ == "__main__":
    unittest.main()
