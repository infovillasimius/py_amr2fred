import unittest

from rdflib import Graph, URIRef, Literal

from py_amr2fred.glossary import Glossary
from py_amr2fred.node import Node
from py_amr2fred.rdf_writer import RdfWriter


class TestRdfWriter(unittest.TestCase):

    def setUp(self):
        """Initialize an RdfWriter instance before each test."""
        self.writer = RdfWriter()

    def test_new_graph_initialization(self):
        """Test if a new graph is correctly initialized."""
        self.assertIsInstance(self.writer.graph, Graph)
        self.assertIsInstance(self.writer.not_visible_graph, Graph)
        self.assertGreater(len(list(self.writer.graph.namespaces())), 0)  # Should have bound namespaces

    def test_get_prefixes(self):
        """Test if the correct prefixes are returned."""
        prefixes = self.writer.get_prefixes()
        self.assertTrue(isinstance(prefixes, list))
        self.assertGreater(len(prefixes), 0)
        self.assertTrue(all(len(item) == 2 for item in prefixes))  # Each prefix should be a tuple (prefix, namespace)

    def test_get_uri_standard(self):
        """Test URI generation for normal variables."""
        test_var = "exampleVar"
        expected_uri = Glossary.FRED_NS + test_var
        self.assertEqual(self.writer.get_uri(test_var), expected_uri)

    def test_get_uri_prefixed(self):
        """Test URI generation for prefixed variables."""
        test_var = Glossary.DUL
        expected_uri = Glossary.DUL_NS
        self.assertEqual(self.writer.get_uri(test_var), expected_uri)

    def test_get_uri_blank_node(self):
        """Test URI generation for blank nodes."""
        test_var = "_:blankNode"
        self.assertEqual(self.writer.get_uri(test_var), test_var)

    def test_to_rdf(self):
        """Test converting a simple Node structure to RDF."""
        root = Node("entity1", Glossary.TOP)
        child1 = Node("entity2", relation="hasRelation")
        child2 = Node("entity3", relation="hasOtherRelation")

        root.node_list.append(child1)
        root.node_list.append(child2)

        self.writer.to_rdf(root)

        # Expected triples
        s1 = URIRef(Glossary.FRED_NS + "entity1")
        p1 = URIRef(Glossary.FRED_NS + "hasRelation")
        o1 = Literal("entity2", datatype=Glossary.STRING_SCHEMA_NS)  # Expected as a Literal

        p2 = URIRef(Glossary.FRED_NS + "hasOtherRelation")
        o2 = Literal("entity3", datatype=Glossary.STRING_SCHEMA_NS)

        # Assertions
        self.assertIn((s1, p1, o1), self.writer.graph)  # Ensure entity2 is a Literal
        self.assertIn((s1, p2, o2), self.writer.graph)  # Ensure entity3 is a Literal

        # Debugging: Print triples in the graph
        print("Generated triples in graph:")
        for triple in self.writer.graph:
            print(triple)

    def test_serialize_nt_format(self):
        """Test serialization of the RDF graph in N-Triples format."""
        root = Node("entity1", Glossary.TOP)
        root.node_list.append(Node("entity2", relation="hasRelation"))
        self.writer.to_rdf(root)

        serialized_graph = self.writer.serialize(Glossary.RdflibMode.NT)
        self.assertIsInstance(serialized_graph, str)
        self.assertTrue(serialized_graph.strip().endswith("."))  # N-Triples statements end with a dot

    def test_serialize_turtle_format(self):
        """Test serialization of the RDF graph in Turtle format."""
        root = Node("entity1", Glossary.TOP)
        root.node_list.append(Node("entity2", relation="hasRelation"))
        self.writer.to_rdf(root)

        serialized_graph = self.writer.serialize(Glossary.RdflibMode.TURTLE)
        self.assertIsInstance(serialized_graph, str)
        self.assertIn("@prefix", serialized_graph)  # Turtle format includes prefixes


if __name__ == "__main__":
    unittest.main()
