"""
URI Builder Utility

This module provides a centralized utility for URI construction logic,
consolidating similar URI building logic that was scattered across multiple files.
"""

from typing import Optional, Dict, Any
from urllib.parse import quote, urlencode
import re

from .config_manager import ConfigurationManager


class URIBuilder:
    """
    Utility class for building URIs with proper encoding and namespace handling.
    
    This class consolidates URI construction logic previously scattered across:
    - rdf_writer.py lines 102-119
    - amr2fred.py lines 32-36  
    - taf_post_processor.py lines 35-38
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """
        Initialize URI builder.
        
        Args:
            config_manager: Configuration manager instance. If None, gets singleton instance.
        """
        self.config = config_manager or ConfigurationManager.get_instance()
    
    def build_namespace_uri(self, prefix: str, local_name: str) -> str:
        """
        Build a complete URI from a namespace prefix and local name.
        
        Args:
            prefix: Namespace prefix (without colon)
            local_name: Local name part
            
        Returns:
            Complete URI string
            
        Example:
            builder.build_namespace_uri("fred", "Entity") -> "http://www.ontology.../Entity"
        """
        namespace = self.config.namespaces.get_namespace(prefix)
        if namespace:
            return f"{namespace}{local_name}"
        else:
            # Fallback to prefixed form if namespace not found
            return f"{prefix}:{local_name}"
    
    def resolve_prefixed_uri(self, prefixed_uri: str) -> str:
        """
        Resolve a prefixed URI to its full form.
        
        Args:
            prefixed_uri: URI in prefix:local format
            
        Returns:
            Full URI or original string if no prefix found
        """
        return self.config.namespaces.resolve_prefixed_name(prefixed_uri)
    
    def build_api_url(self, endpoint_type: str, variant: str = 'default', 
                      params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build API endpoint URL with query parameters.
        
        Args:
            endpoint_type: Type of endpoint (e.g., 'text2amr', 'multilingualAmr')
            variant: Endpoint variant (default, spring, usea, etc.)
            params: Query parameters to append
            
        Returns:
            Complete API URL
        """
        if endpoint_type == 'text2amr':
            base_url = self.config.api.get_text2amr_endpoint(variant)
        elif endpoint_type == 'multilingualAmr':
            base_url = self.config.api.get_multilingual_amr_endpoint(variant)
        else:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")
        
        if not base_url:
            raise ValueError(f"No URL configured for {endpoint_type}:{variant}")
        
        if params:
            # Handle different parameter encoding styles
            if endpoint_type == 'text2amr' and 'sentence' in params:
                # For text2amr, sentence is typically directly appended
                encoded_sentence = quote(params['sentence'])
                return f"{base_url}{encoded_sentence}"
            else:
                # For other endpoints, use standard query parameters
                query_string = urlencode(params)
                separator = '&' if '?' in base_url else '?'
                return f"{base_url}{separator}{query_string}"
        
        return base_url
    
    def sanitize_local_name(self, name: str) -> str:
        """
        Sanitize a string to be used as a URI local name.
        
        Args:
            name: String to sanitize
            
        Returns:
            Sanitized string safe for URI use
        """
        # Remove or replace problematic characters
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        
        return sanitized
    
    def build_instance_uri(self, prefix: str, instance_type: str, 
                          identifier: Optional[str] = None) -> str:
        """
        Build a URI for an instance of a given type.
        
        Args:
            prefix: Namespace prefix
            instance_type: Type of the instance
            identifier: Optional unique identifier
            
        Returns:
            Instance URI
        """
        if identifier:
            local_name = f"{instance_type}_{self.sanitize_local_name(identifier)}"
        else:
            local_name = instance_type
            
        return self.build_namespace_uri(prefix, local_name)
    
    def build_property_uri(self, prefix: str, property_name: str) -> str:
        """
        Build a URI for a property/relation.
        
        Args:
            prefix: Namespace prefix
            property_name: Name of the property
            
        Returns:
            Property URI
        """
        sanitized_name = self.sanitize_local_name(property_name)
        return self.build_namespace_uri(prefix, sanitized_name)


class GraphFactory:
    """
    Factory class for creating and initializing RDF graphs.
    
    This class consolidates graph initialization patterns previously scattered across:
    - rdf_writer.py lines 27-35
    - taf_post_processor.py lines 40-76
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """
        Initialize graph factory.
        
        Args:
            config_manager: Configuration manager instance. If None, gets singleton instance.
        """
        self.config = config_manager or ConfigurationManager.get_instance()
        self.uri_builder = URIBuilder(config_manager)
    
    def create_graph(self, bind_namespaces: bool = True, 
                    custom_namespaces: Optional[Dict[str, str]] = None) -> 'rdflib.Graph':
        """
        Create and initialize an RDF graph.
        
        Args:
            bind_namespaces: Whether to bind default namespaces
            custom_namespaces: Additional custom namespaces to bind
            
        Returns:
            Initialized RDF graph
        """
        try:
            from rdflib import Graph
        except ImportError:
            raise ImportError("rdflib is required for graph operations")
        
        graph = Graph()
        
        if bind_namespaces:
            self._bind_default_namespaces(graph)
        
        if custom_namespaces:
            for prefix, namespace in custom_namespaces.items():
                graph.bind(prefix, namespace)
        
        return graph
    
    def create_graph_pair(self, bind_namespaces: bool = True) -> tuple['rdflib.Graph', 'rdflib.Graph']:
        """
        Create a pair of graphs (main and not-visible).
        
        This pattern is used in several places where two graphs are needed.
        
        Args:
            bind_namespaces: Whether to bind default namespaces
            
        Returns:
            Tuple of (main_graph, not_visible_graph)
        """
        main_graph = self.create_graph(bind_namespaces)
        not_visible_graph = self.create_graph(bind_namespaces)
        
        return main_graph, not_visible_graph
    
    def _bind_default_namespaces(self, graph: 'rdflib.Graph') -> None:
        """
        Bind default namespaces to a graph.
        
        Args:
            graph: RDF graph to bind namespaces to
        """
        all_prefixes = self.config.namespaces.get_all_prefixes()
        
        for prefix, namespace in all_prefixes.items():
            try:
                graph.bind(prefix, namespace)
            except Exception as e:
                # Log warning but don't fail the entire operation
                import logging
                logging.getLogger(__name__).warning(
                    f"Failed to bind namespace {prefix}: {namespace} - {e}"
                )
    
    def clone_graph_structure(self, source_graph: 'rdflib.Graph') -> 'rdflib.Graph':
        """
        Clone the namespace bindings from one graph to another.
        
        Args:
            source_graph: Graph to copy namespaces from
            
        Returns:
            New graph with same namespace bindings
        """
        new_graph = self.create_graph(bind_namespaces=False)
        
        # Copy namespace bindings
        for prefix, namespace in source_graph.namespaces():
            new_graph.bind(prefix, namespace)
        
        return new_graph