"""
Configuration Management System for py_amr2fred

This module provides a centralized configuration management system that replaces
the large Glossary class with a more maintainable JSON-based approach.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ConfigurationManager:
    """
    Centralized management of namespaces, prefixes, patterns, and configuration values.
    
    Consolidates configuration previously scattered across the Glossary class
    into a JSON-based, runtime-reloadable system.
    """
    
    _instance: Optional['ConfigurationManager'] = None
    _config_cache: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Path to configuration directory. If None, uses default config/ directory.
        """
        self._config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self._namespace_manager = NamespaceManager(self)
        self._pattern_matcher = AMRPatternMatcher(self)
        self._linguistic_provider = LinguisticDataProvider(self)
        self._entity_classifier = EntityClassifier(self)
        self._validation_service = ValidationService(self)
        self._api_manager = APIEndpointManager(self)
        self._data_sources = DataSourceManager(self)
        
    @staticmethod
    def get_instance(config_dir: Optional[str] = None) -> 'ConfigurationManager':
        """
        Get singleton instance of ConfigurationManager.
        
        Args:
            config_dir: Path to configuration directory.
            
        Returns:
            ConfigurationManager instance
        """
        if ConfigurationManager._instance is None:
            ConfigurationManager._instance = ConfigurationManager(config_dir)
        return ConfigurationManager._instance
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory path."""
        current_dir = Path(__file__).parent
        return current_dir / "config"
    
    def load_config(self, config_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load a configuration file.
        
        Args:
            config_name: Name of the configuration file (without .json extension)
            force_reload: Force reload even if cached
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration file is invalid JSON
        """
        if config_name in self._config_cache and not force_reload:
            return self._config_cache[config_name]
            
        config_path = self._config_dir / f"{config_name}.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._config_cache[config_name] = config
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration {config_path}: {e}")
            raise
    
    def reload_all(self):
        """Reload all cached configurations."""
        self._config_cache.clear()
    
    @property
    def namespaces(self) -> 'NamespaceManager':
        """Get namespace manager."""
        return self._namespace_manager
    
    @property
    def patterns(self) -> 'AMRPatternMatcher':
        """Get AMR pattern matcher."""
        return self._pattern_matcher
    
    @property
    def linguistics(self) -> 'LinguisticDataProvider':
        """Get linguistic data provider."""
        return self._linguistic_provider
    
    @property
    def entities(self) -> 'EntityClassifier':
        """Get entity classifier."""
        return self._entity_classifier
    
    @property
    def validation(self) -> 'ValidationService':
        """Get validation service."""
        return self._validation_service
    
    @property
    def api(self) -> 'APIEndpointManager':
        """Get API endpoint manager."""
        return self._api_manager
        
    @property
    def data_sources(self) -> 'DataSourceManager':
        """Get data source manager."""
        return self._data_sources


class NamespaceManager:
    """Manages namespace resolution and prefix management."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._namespaces_config = None
        self._ontology_config = None
    
    @property
    def namespaces_config(self) -> Dict[str, Any]:
        """Get namespaces configuration."""
        if self._namespaces_config is None:
            self._namespaces_config = self._config_manager.load_config('namespaces')
        return self._namespaces_config
    
    @property
    def ontology_config(self) -> Dict[str, Any]:
        """Get ontology mappings configuration."""
        if self._ontology_config is None:
            self._ontology_config = self._config_manager.load_config('ontology_mappings')
        return self._ontology_config
    
    def get_namespace(self, prefix: str) -> Optional[str]:
        """
        Get namespace URI for a given prefix.
        
        Args:
            prefix: The prefix to look up
            
        Returns:
            Namespace URI or None if not found
        """
        prefixes = self.namespaces_config.get('prefixes', {})
        standard_prefixes = self.namespaces_config.get('standardPrefixes', {})
        
        return prefixes.get(prefix) or standard_prefixes.get(prefix)
    
    def get_all_prefixes(self) -> Dict[str, str]:
        """Get all prefix to namespace mappings."""
        prefixes = self.namespaces_config.get('prefixes', {}).copy()
        prefixes.update(self.namespaces_config.get('standardPrefixes', {}))
        return prefixes
    
    def get_prefix_list(self) -> List[str]:
        """Get list of all prefixes with colon suffix."""
        prefixes = self.get_all_prefixes()
        return [f"{prefix}:" for prefix in prefixes.keys()]
    
    def get_namespace_list(self) -> List[str]:
        """Get list of all namespace URIs."""
        prefixes = self.get_all_prefixes()
        return list(prefixes.values())
    
    def resolve_prefixed_name(self, prefixed_name: str) -> str:
        """
        Resolve a prefixed name to full URI.
        
        Args:
            prefixed_name: Name with prefix (e.g., 'fred:Entity')
            
        Returns:
            Full URI or original name if prefix not found
        """
        if ':' not in prefixed_name:
            return prefixed_name
            
        prefix, local_name = prefixed_name.split(':', 1)
        namespace = self.get_namespace(prefix)
        
        if namespace:
            return f"{namespace}{local_name}"
        return prefixed_name


class AMRPatternMatcher:
    """Manages AMR pattern matching and relations."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._patterns_config = None
    
    @property
    def patterns_config(self) -> Dict[str, Any]:
        """Get AMR patterns configuration."""
        if self._patterns_config is None:
            self._patterns_config = self._config_manager.load_config('amr_patterns')
        return self._patterns_config
    
    def get_pattern(self, pattern_name: str) -> Optional[str]:
        """Get a regex pattern by name."""
        return self.patterns_config.get('patterns', {}).get(pattern_name)
    
    def get_relation(self, category: str, relation_name: str) -> Optional[str]:
        """Get a relation string by category and name."""
        relations = self.patterns_config.get('relations', {})
        return relations.get(category, {}).get(relation_name)
    
    def get_special_verb(self, verb_name: str) -> Optional[str]:
        """Get a special verb by name."""
        return self.patterns_config.get('specialVerbs', {}).get(verb_name)
    
    def get_fred_mapping(self, amr_relation: str) -> Optional[str]:
        """Get FRED mapping for AMR relation."""
        mappings = self.patterns_config.get('mappings', {})
        return mappings.get('relationsToFred', {}).get(amr_relation)
    
    def get_constant(self, constant_name: str) -> Any:
        """Get a constant value by name."""
        return self.patterns_config.get('constants', {}).get(constant_name)


class LinguisticDataProvider:
    """Provides linguistic data (adjectives, adverbs, etc.)."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._linguistic_config = None
        self._adjectives = None
    
    @property
    def linguistic_config(self) -> Dict[str, Any]:
        """Get linguistic data configuration."""
        if self._linguistic_config is None:
            self._linguistic_config = self._config_manager.load_config('linguistic_data')
        return self._linguistic_config
    
    def get_pronouns(self, category: str) -> List[str]:
        """Get pronouns by category (person, male, female, thing, etc.)."""
        return self.linguistic_config.get('pronouns', {}).get(category, [])
    
    def get_conjunctions(self) -> List[str]:
        """Get list of conjunctions."""
        return self.linguistic_config.get('conjunctions', [])
    
    def get_prepositions(self) -> List[str]:
        """Get list of prepositions."""
        return self.linguistic_config.get('prepositions', [])
    
    def get_manner_adverbs(self) -> List[str]:
        """Get list of manner adverbs."""
        return self.linguistic_config.get('mannerAdverbs', [])
    
    def get_adjectives(self) -> List[str]:
        """Get list of adjectives from external JSON file."""
        if self._adjectives is None:
            try:
                adjectives_file = self.linguistic_config.get('adjectivesFile', 'adjectives.json')
                current_dir = Path(__file__).parent
                adjectives_path = current_dir / adjectives_file
                
                with open(adjectives_path, 'r', encoding='utf-8') as f:
                    self._adjectives = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load adjectives: {e}")
                self._adjectives = []
        
        return self._adjectives


class EntityClassifier:
    """Manages entity classification and type checking."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._entities_config = None
    
    @property
    def entities_config(self) -> Dict[str, Any]:
        """Get AMR entities configuration."""
        if self._entities_config is None:
            self._entities_config = self._config_manager.load_config('amr_entities')
        return self._entities_config
    
    def get_entity_types(self, category: str) -> List[str]:
        """Get entity types by category."""
        return self.entities_config.get('namedEntities', {}).get(category, [])
    
    def get_special_entities(self) -> List[str]:
        """Get list of special entities."""
        return self.entities_config.get('specialEntities', [])
    
    def get_quantity_types(self) -> List[str]:
        """Get list of quantity types."""
        return self.entities_config.get('quantityTypes', [])
    
    def get_date_component(self, component: str) -> Optional[str]:
        """Get date component pattern."""
        return self.entities_config.get('dateComponents', {}).get(component)
    
    def is_named_entity(self, entity: str) -> bool:
        """Check if string is a known named entity."""
        for category_entities in self.entities_config.get('namedEntities', {}).values():
            if entity in category_entities:
                return True
        return entity in self.get_special_entities()


class ValidationService:
    """Handles pattern validation and data type checking."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._validation_config = None
    
    @property
    def validation_config(self) -> Dict[str, Any]:
        """Get validation patterns configuration."""
        if self._validation_config is None:
            self._validation_config = self._config_manager.load_config('validation_patterns')
        return self._validation_config
    
    def get_data_type_info(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Get data type validation info."""
        return self.validation_config.get('dataTypes', {}).get(data_type)
    
    def get_serialization_formats(self) -> List[str]:
        """Get list of supported serialization formats."""
        return self.validation_config.get('serializationFormats', [])
    
    def validate_pattern(self, value: str, data_type: str) -> bool:
        """
        Validate a value against a data type pattern.
        
        Args:
            value: Value to validate
            data_type: Data type to validate against
            
        Returns:
            True if value matches pattern, False otherwise
        """
        type_info = self.get_data_type_info(data_type)
        if not type_info or not type_info.get('pattern'):
            return True
        
        import re
        pattern = type_info['pattern']
        return bool(re.match(pattern, value))


class APIEndpointManager:
    """Manages external API endpoint configuration."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._api_config = None
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """Get API endpoints configuration."""
        if self._api_config is None:
            self._api_config = self._config_manager.load_config('api_endpoints')
        return self._api_config
    
    def get_text2amr_endpoint(self, variant: str = 'default') -> Optional[str]:
        """Get text-to-AMR API endpoint."""
        return self.api_config.get('text2amr', {}).get(variant)
    
    def get_multilingual_amr_endpoint(self, variant: str = 'default') -> Optional[str]:
        """Get multilingual AMR API endpoint."""
        return self.api_config.get('multilingualAmr', {}).get(variant)
    
    def get_request_config(self) -> Dict[str, Any]:
        """Get request configuration (timeout, headers, etc.)."""
        return self.api_config.get('requestConfig', {})


class DataSourceManager:
    """Manages data file paths and metadata."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._data_config = None
    
    @property
    def data_config(self) -> Dict[str, Any]:
        """Get data sources configuration."""
        if self._data_config is None:
            self._data_config = self._config_manager.load_config('data_sources')
        return self._data_config
    
    def get_propbank_config(self) -> Dict[str, Any]:
        """Get PropBank data configuration."""
        return self.data_config.get('propbank', {})
    
    def get_data_path(self, path_type: str) -> Optional[str]:
        """Get data path by type."""
        return self.data_config.get('dataPaths', {}).get(path_type)
    
    def resolve_data_file_path(self, relative_path: str) -> Path:
        """
        Resolve a relative data file path to absolute path.
        
        Args:
            relative_path: Relative path from project root
            
        Returns:
            Absolute Path object
        """
        project_root = Path(__file__).parent.parent
        return project_root / relative_path


# Maintain backwards compatibility with Glossary enum classes
class RdflibMode(Enum):
    """
    Enumeration of RDF serialization formats supported by rdflib.
    """
    JSON_LD = "json-ld"
    N3 = "n3"
    NT = "nt"
    XML = "xml"
    TURTLE = "turtle"


class NodeType(Enum):
    """
    Enumeration of node types in an AMR graph.
    """
    NOUN = 0
    VERB = 1
    OTHER = 2
    AMR2FRED = 3
    FRED = 4
    COMMON = 5


class NodeStatus(Enum):
    """
    Enumeration of node statuses used in the AMR parsing process.
    """
    OK = 0
    AMR = 1
    ERROR = 2
    REMOVE = 3


class PropbankFrameFields(Enum):
    """
    Enumeration of field names in the PropBank frame table.
    """
    PB_Frame = 0
    PB_FrameLabel = 1
    PB_Role = 2
    FN_Frame = 3
    VA_Frame = 4


class PropbankRoleFields(Enum):
    """
    Enumeration of field names in the PropBank role table.
    """
    PB_Frame = 0
    PB_Role = 1
    PB_RoleLabel = 2
    PB_GenericRole = 3
    PB_Tr = 4
    PB_ARG = 5
    VA_Role = 6