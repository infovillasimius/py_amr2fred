"""Tests for URI builder and GraphFactory."""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from py_amr2fred.uri_builder import URIBuilder, GraphFactory
from py_amr2fred.config_manager import ConfigurationManager


class TestURIBuilder(unittest.TestCase):

    def setUp(self):
        """Set up test URI builder."""
        config_dir = str((Path(__file__).parent.parent / "py_amr2fred" / "config").resolve())
        self.config = ConfigurationManager(config_dir)
        self.uri_builder = URIBuilder(self.config)

    def test_build_namespace_uri(self):
        """Test building namespace URIs."""
        uri = self.uri_builder.build_namespace_uri("fred", "Entity")
        self.assertTrue(uri.startswith("http://"))
        self.assertTrue(uri.endswith("Entity"))
        
        # Test with unknown prefix
        uri = self.uri_builder.build_namespace_uri("unknown", "Entity")
        self.assertEqual(uri, "unknown:Entity")

    def test_resolve_prefixed_uri(self):
        """Test resolving prefixed URIs."""
        resolved = self.uri_builder.resolve_prefixed_uri("owl:Thing")
        self.assertTrue(resolved.startswith("http://"))
        self.assertTrue(resolved.endswith("Thing"))

    def test_build_api_url(self):
        """Test building API URLs."""
        url = self.uri_builder.build_api_url("text2amr", params={"sentence": "hello world"})
        self.assertTrue(url.startswith("http"))
        self.assertIn("hello%20world", url)  # URL encoded
        
        # Test multilingual endpoint
        url = self.uri_builder.build_api_url("multilingualAmr")
        self.assertTrue(url.startswith("http"))

    def test_sanitize_local_name(self):
        """Test local name sanitization."""
        sanitized = self.uri_builder.sanitize_local_name("hello world")
        self.assertEqual(sanitized, "hello_world")
        
        sanitized = self.uri_builder.sanitize_local_name("123test")
        self.assertEqual(sanitized, "_123test")  # Should not start with number

    def test_build_instance_uri(self):
        """Test building instance URIs."""
        uri = self.uri_builder.build_instance_uri("fred", "Person", "john")
        self.assertTrue(uri.startswith("http://"))
        self.assertIn("Person_john", uri)

    def test_build_property_uri(self):
        """Test building property URIs."""
        uri = self.uri_builder.build_property_uri("dul", "hasQuality")
        self.assertTrue(uri.startswith("http://"))
        self.assertIn("hasQuality", uri)


class TestGraphFactory(unittest.TestCase):

    def setUp(self):
        """Set up test graph factory."""
        from pathlib import Path
        config_dir = str((Path(__file__).parent.parent / "py_amr2fred" / "config").resolve())
        self.config = ConfigurationManager(config_dir)
        self.graph_factory = GraphFactory(self.config)

    @patch('rdflib.Graph')
    def test_create_graph(self, mock_graph_class):
        """Test graph creation."""
        mock_graph = Mock()
        mock_graph_class.return_value = mock_graph
        
        graph = self.graph_factory.create_graph()
        
        # Verify graph was created
        mock_graph_class.assert_called_once()
        self.assertEqual(graph, mock_graph)
        
        # Verify namespaces were bound (should have been called multiple times)
        self.assertTrue(mock_graph.bind.called)

    @patch('rdflib.Graph')
    def test_create_graph_pair(self, mock_graph_class):
        """Test creating a pair of graphs."""
        mock_graph1 = Mock()
        mock_graph2 = Mock()
        mock_graph_class.side_effect = [mock_graph1, mock_graph2]
        
        main_graph, not_visible_graph = self.graph_factory.create_graph_pair()
        
        # Verify both graphs were created
        self.assertEqual(mock_graph_class.call_count, 2)
        self.assertEqual(main_graph, mock_graph1)
        self.assertEqual(not_visible_graph, mock_graph2)

    @patch('rdflib.Graph')
    def test_clone_graph_structure(self, mock_graph_class):
        """Test cloning graph structure."""
        # Create mock source graph
        mock_source = Mock()
        mock_source.namespaces.return_value = [("fred", "http://example.com/fred"), ("dul", "http://example.com/dul")]
        
        # Create mock new graph
        mock_new_graph = Mock()
        mock_graph_class.return_value = mock_new_graph
        
        cloned = self.graph_factory.clone_graph_structure(mock_source)
        
        # Verify new graph was created
        mock_graph_class.assert_called_once()
        self.assertEqual(cloned, mock_new_graph)
        
        # Verify namespaces were copied
        self.assertEqual(mock_new_graph.bind.call_count, 2)


if __name__ == '__main__':
    from pathlib import Path
    unittest.main()