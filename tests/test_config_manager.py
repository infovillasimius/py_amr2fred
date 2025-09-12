"""Tests for ConfigurationManager and related components."""

import unittest
import tempfile
import json
import os
from pathlib import Path

from py_amr2fred.config_manager import (
    ConfigurationManager, NamespaceManager, AMRPatternMatcher,
    LinguisticDataProvider, EntityClassifier, ValidationService,
    APIEndpointManager, DataSourceManager
)


class TestConfigurationManager(unittest.TestCase):

    def setUp(self):
        """Set up test configuration manager."""
        # Use the actual config directory for testing
        config_dir = Path(__file__).parent.parent / "py_amr2fred" / "config"
        self.config = ConfigurationManager(str(config_dir))

    def test_singleton_pattern(self):
        """Test that ConfigurationManager follows singleton pattern."""
        config1 = ConfigurationManager.get_instance()
        config2 = ConfigurationManager.get_instance()
        self.assertIs(config1, config2)

    def test_namespace_loading(self):
        """Test namespace configuration loading."""
        namespaces = self.config.namespaces.get_all_prefixes()
        self.assertIn("fred", namespaces)
        self.assertIn("dul", namespaces)
        self.assertIn("owl", namespaces)

    def test_namespace_resolution(self):
        """Test namespace resolution."""
        fred_ns = self.config.namespaces.get_namespace("fred")
        self.assertEqual(fred_ns, "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")
        
        resolved = self.config.namespaces.resolve_prefixed_name("fred:Entity")
        self.assertTrue(resolved.startswith("http://"))

    def test_pattern_matching(self):
        """Test AMR pattern matching."""
        verb_pattern = self.config.patterns.get_pattern("verb")
        self.assertEqual(verb_pattern, "-[0-9]+$")
        
        polarity_relation = self.config.patterns.get_relation("core", "polarity")
        self.assertEqual(polarity_relation, ":polarity")

    def test_linguistic_data(self):
        """Test linguistic data access."""
        person_pronouns = self.config.linguistics.get_pronouns("person")
        self.assertIn("I", person_pronouns)
        self.assertIn("you", person_pronouns)
        
        conjunctions = self.config.linguistics.get_conjunctions()
        self.assertIn("and", conjunctions)

    def test_entity_classification(self):
        """Test entity classification."""
        person_entities = self.config.entities.get_entity_types("person")
        self.assertIn("person", person_entities)
        self.assertIn("family", person_entities)

    def test_validation_service(self):
        """Test validation service."""
        formats = self.config.validation.get_serialization_formats()
        self.assertIn("turtle", formats)
        self.assertIn("json-ld", formats)

    def test_api_endpoints(self):
        """Test API endpoint configuration."""
        text2amr_endpoint = self.config.api.get_text2amr_endpoint()
        self.assertIsNotNone(text2amr_endpoint)
        self.assertTrue(text2amr_endpoint.startswith("http"))

    def test_data_sources(self):
        """Test data source configuration."""
        propbank_config = self.config.data_sources.get_propbank_config()
        self.assertIn("roleMatrix", propbank_config)
        self.assertIn("frameMatrix", propbank_config)


class TestNamespaceManager(unittest.TestCase):

    def setUp(self):
        """Set up test namespace manager."""
        config_dir = Path(__file__).parent.parent / "py_amr2fred" / "config"
        config = ConfigurationManager(str(config_dir))
        self.namespace_mgr = config.namespaces

    def test_get_namespace(self):
        """Test getting namespace by prefix."""
        fred_ns = self.namespace_mgr.get_namespace("fred")
        self.assertEqual(fred_ns, "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#")

    def test_get_all_prefixes(self):
        """Test getting all prefixes."""
        prefixes = self.namespace_mgr.get_all_prefixes()
        self.assertIsInstance(prefixes, dict)
        self.assertGreater(len(prefixes), 20)  # Should have many prefixes

    def test_resolve_prefixed_name(self):
        """Test resolving prefixed names to full URIs."""
        resolved = self.namespace_mgr.resolve_prefixed_name("owl:Thing")
        self.assertTrue(resolved.endswith("Thing"))
        self.assertTrue(resolved.startswith("http://"))


if __name__ == '__main__':
    unittest.main()