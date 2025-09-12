# py_amr2fred Package Documentation

A Python library for transforming Abstract Meaning Representation (AMR) into RDF (Resource Description Framework) representations compliant with OWL ontologies. This package provides a comprehensive toolkit for parsing AMR graphs, converting them to semantic RDF knowledge graphs, and enriching them with external knowledge sources.

## Package Overview

The `py_amr2fred` package consists of several interconnected modules that work together to convert AMR representations into RDF knowledge graphs:

### Core Components

- **`amr2fred.py`**: Main orchestrator class that coordinates the entire conversion process
- **`node.py`**: Refactored node system with separated concerns for better maintainability
- **`parser.py`**: AMR string parsing and node tree construction
- **`rdf_writer.py`**: RDF graph generation and serialization
- **`glossary.py`**: Constants, patterns, and configuration management
- **`taf_post_processor.py`**: Post-processing for knowledge enrichment and disambiguation

### Supporting Components

- **`node_core.py`**: Basic node data and identity management
- **`node_relations.py`**: Parent-child relationship management
- **`config_manager.py`**: Configuration and pattern matching
- **`propbank.py`**: PropBank frame and role integration
- **`digraph_writer.py`**: Graph visualization support
- **`uri_builder.py`**: URI construction utilities
- **`couple.py`**: Node relationship pairs
- **`singleton_mixin.py`**: Singleton pattern implementation
- **`exception_handler.py`**: Error handling and recursion protection

## Class Hierarchy

```mermaid
classDiagram
    class Amr2fred {
        +Parser parser
        +RdfWriter writer
        +Glossary glossary
        +TafPostProcessor taf
        +translate(amr, text, mode, serialize) str|Graph
        +get_amr(text, alt_api, multilingual) str
    }

    class Node {
        +NodeCore core
        +NodeRelations relations
        +str var
        +str relation
        +NodeStatus status
        +bool visibility
        +add_child(child) void
        +get_children() List~Node~
        +find_by_var(var) Node
        +depth_first_search(predicate) Node
        +copy(mode) Node
    }

    class NodeCore {
        +str var
        +str relation
        +int node_id
        +str label
        +str verb
        +NodeStatus status
        +NodeType node_type
        +bool visibility
        +bool prefix
        +bool malformed
    }

    class NodeRelations {
        +List~Node~ node_list
        +Node parent
        +List~Node~ parent_list
        +add_child(child) void
        +remove_child(child) void
        +get_children() List~Node~
        +has_parent() bool
        +is_root() bool
        +is_leaf() bool
    }

    class Parser {
        +List~Node~ nodes
        +List~Couple~ couples
        +parse(amr_string) Node
        +preprocess(amr) str
        +create_node_tree() Node
        +handle_multi_sentence() void
    }

    class RdfWriter {
        +Graph graph
        +Graph not_visible_graph
        +NamespaceManager namespace_manager
        +to_rdf(root_node) void
        +serialize(mode) str
        +add_triple(subject, predicate, object) void
    }

    class Glossary {
        +Dict constants
        +List~str~ NAMESPACE
        +List~str~ PREFIX
        +str FRED_NS
        +AMR_* patterns
        +get_constant(key) str
        +load_configuration() void
    }

    class TafPostProcessor {
        +disambiguate(text, graph) Graph
        +disambiguate_usea(text, graph) Graph
        +link_to_wikidata(graph) Graph
    }

    class DigraphWriter {
        +to_png(graph, not_visible_graph) IO
        +to_svg_string(graph, not_visible_graph) str
        +create_digraph(root_node) str
    }

    class Propbank {
        +Dict frame_data
        +Dict role_data
        +get_frame_info(predicate) Dict
        +get_role_mapping(frame, role) str
        +load_propbank_data() void
    }

    class ConfigurationManager {
        +NamespaceManager namespaces
        +AMRPatternMatcher patterns
        +EntityClassifier classifier
        +ValidationService validator
        +get_instance() ConfigurationManager
    }

    class Couple {
        +Node first
        +Node second
        +str relation_type
        +equals(other) bool
    }

    class URIBuilder {
        +build_uri(base, fragment) str
        +build_fred_uri(fragment) str
        +build_ontology_uri(concept) str
        +normalize_fragment(text) str
    }

    class SingletonMixin {
        +get_instance() Self
        +_instances Dict
    }

    %% Enums
    class RdflibMode {
        <<enumeration>>
        TURTLE
        NT
        XML
        JSON_LD
        N3
    }

    class NodeStatus {
        <<enumeration>>
        AMR
        FRED
        REMOVE
        TO_REMOVE
    }

    class NodeType {
        <<enumeration>>
        CONCEPT
        ENTITY
        LITERAL
        OTHER
    }

    class CopyMode {
        <<enumeration>>
        SHALLOW
        DEEP
        STRUCTURE_ONLY
        CHILDREN_ONLY
    }

    %% Relationships
    Amr2fred --> Parser : uses
    Amr2fred --> RdfWriter : uses
    Amr2fred --> Glossary : uses
    Amr2fred --> TafPostProcessor : uses

    Node --> NodeCore : contains
    Node --> NodeRelations : contains
    NodeRelations --> Node : manages

    Parser --> Node : creates
    Parser --> Couple : creates
    Parser --> Glossary : uses
    Parser --> SingletonMixin : inherits

    RdfWriter --> Node : processes
    RdfWriter --> Glossary : uses
    RdfWriter --> URIBuilder : uses

    TafPostProcessor --> Propbank : uses

    ConfigurationManager --> Glossary : configures

    Glossary --> RdflibMode : defines
    Glossary --> NodeStatus : defines
    Glossary --> NodeType : defines

    Node --> CopyMode : uses

    Propbank --> SingletonMixin : inherits
```

## Module Details

### amr2fred.py
The main orchestrator class that coordinates the entire AMR to RDF conversion process.

**Key Features:**
- Integrates parsing, RDF generation, and post-processing
- Supports multiple output formats (serialized strings or RDFLib Graph objects)
- Handles text-to-AMR conversion via external APIs
- Provides multilingual support
- Generates graphical representations

**Usage:**
```python
from py_amr2fred import Amr2fred, Glossary

amr2fred = Amr2fred()
result = amr2fred.translate(
    amr="(w / want-01 :ARG0 (i / i) :ARG1 (g / go-02 :ARG0 i))",
    mode=Glossary.RdflibMode.TURTLE,
    serialize=True
)
```

### node.py
Refactored node system that combines three separate components for better separation of concerns:

**Components:**
- **NodeCore**: Basic node data and identity
- **NodeRelations**: Parent-child relationships
- **Node**: Main interface combining both components

**Key Features:**
- Improved testability and maintainability
- Backward compatibility with original Node API
- Enhanced tree operations and traversal methods
- Multiple copy modes for different use cases
- Recursion protection for deep trees

### parser.py
Singleton class responsible for parsing AMR strings into hierarchical node structures.

**Key Features:**
- AMR string preprocessing and normalization
- Node tree construction with proper relationships
- Multi-sentence AMR handling
- Integration with PropBank for semantic roles
- Error handling and malformed AMR recovery

### rdf_writer.py
Converts node hierarchies into RDF graphs with proper namespace management.

**Key Features:**
- RDFLib Graph construction
- Namespace binding and management
- Multiple serialization formats
- Visibility-based triple filtering
- URI construction and normalization

### glossary.py
Centralized management of constants, patterns, and configuration data.

**Key Features:**
- AMR pattern definitions
- Namespace and prefix management
- Node status and type enumerations
- Singleton pattern with metaclass support
- Configuration loading and validation

### Node System Architecture

The refactored node system provides better separation of concerns:

#### NodeCore (`node_core.py`)
- Manages basic node attributes (var, relation, label, verb)
- Handles node identity with unique ID generation
- Manages node status and type information
- Provides basic attribute getters and setters

#### NodeRelations (`node_relations.py`)
- Manages parent-child relationships
- Handles hierarchical structure operations
- Provides tree traversal capabilities
- Supports both tree and graph structures
- Includes circular reference detection

#### Node (`node.py`)
- Combines NodeCore and NodeRelations
- Provides backward compatibility with original API
- Implements advanced tree operations
- Supports multiple copy strategies
- Includes search and traversal methods

### Configuration Management

The `config_manager.py` module provides centralized configuration:

**Components:**
- **NamespaceManager**: RDF namespace management
- **AMRPatternMatcher**: Pattern matching for AMR constructs
- **EntityClassifier**: Entity type classification
- **ValidationService**: Input validation
- **APIEndpointManager**: External API configuration

### Post-Processing Pipeline

The `taf_post_processor.py` module enriches RDF graphs:

**Features:**
- Word Sense Disambiguation (WSD)
- Wikidata entity linking
- Knowledge graph enrichment
- Multilingual entity resolution

### Visualization Support

The `digraph_writer.py` module generates visual representations:

**Outputs:**
- PNG images (requires Graphviz)
- SVG strings
- DOT format for custom processing

## Usage Patterns

### Basic AMR Processing
```python
from py_amr2fred import Parser, RdfWriter

parser = Parser.get_parser()
writer = RdfWriter()

root_node = parser.parse(amr_string)
writer.to_rdf(root_node)
rdf_graph = writer.graph
```

### Node Tree Manipulation
```python
from py_amr2fred.node import Node, CopyMode

# Create nodes
parent = Node("p", "TOP")
child = Node("c", "ARG0")

# Build relationships
parent.add_child(child)

# Tree operations
deep_copy = parent.copy(CopyMode.DEEP)
found_node = parent.find_by_var("c")
```

### Configuration Access
```python
from py_amr2fred.config_manager import ConfigurationManager

config = ConfigurationManager.get_instance()
patterns = config.patterns
namespaces = config.namespaces
```

## Design Patterns

The package implements several design patterns:

1. **Singleton Pattern**: Used for Parser, Glossary, and ConfigurationManager
2. **Composition Pattern**: Node combines NodeCore and NodeRelations
3. **Strategy Pattern**: Multiple copy modes and serialization formats
4. **Observer Pattern**: Node relationship management
5. **Factory Pattern**: Graph and URI construction

## Error Handling

The package includes comprehensive error handling:

- **Recursion Protection**: Guards against infinite loops in tree operations
- **Malformed AMR Recovery**: Graceful handling of invalid AMR structures
- **API Failure Handling**: Fallback mechanisms for external services
- **Memory Management**: Efficient handling of large knowledge graphs

## Performance Considerations

- **Lazy Loading**: Configuration and resources loaded on demand
- **Caching**: Frequently used patterns and configurations cached
- **Memory Optimization**: Efficient node storage and relationship management
- **Batch Processing**: Support for processing multiple AMR graphs

## Testing

The package includes comprehensive test coverage:

- Unit tests for individual components
- Integration tests for end-to-end workflows
- Performance tests for large-scale processing
- Mock external API dependencies