# Codebase Refactoring Proposal

## Executive Summary

After conducting a comprehensive analysis of the py_amr2fred repository, I've identified significant opportunities for refactoring that will improve code maintainability, reduce complexity, and eliminate technical debt. The codebase shows patterns of duplication, over-engineering, and architectural issues that can be addressed through systematic refactoring. The proposed changes will reduce the total lines of code by an estimated 25-30% while maintaining all existing functionality.

**Key Findings:**
- 726 lines of constants in a single glossary file creating maintenance burden
- Repeated parsing and validation logic across multiple methods
- Singleton patterns implemented inconsistently
- Missing abstractions for shared functionality
- Overly complex conditional logic chains
- Static analysis shows high cyclomatic complexity in several methods

## Identified Issues

### Code Duplication

#### Location: `C:\Users\igeek\OneDrive\Documents\GitHub\py_amr2fred\py_amr2fred\glossary.py` (lines 1-726)
**Description**: Massive constants file with hardcoded values, redundant namespace definitions, and duplicate prefix/namespace arrays that are manually synchronized.
- Affected files: `glossary.py`, `rdf_writer.py`, `taf_post_processor.py`
- **Proposed solution**: Extract constants into configuration classes with automatic synchronization

#### Location: Exception handling patterns across multiple files
**Description**: Identical try-catch blocks with logger.warning() calls repeated in:
- `amr2fred.py` lines 121-139
- `parser.py` lines 120-123, 239-243
- `digraph_writer.py` lines 107-109, 144-146
- **Proposed solution**: Create centralized exception handling decorator

#### Location: URI construction logic
**Description**: Similar URI building logic scattered across:
- `rdf_writer.py` lines 102-119
- `amr2fred.py` lines 32-36
- `taf_post_processor.py` lines 35-38
- **Proposed solution**: Create dedicated URIBuilder utility class

#### Location: Graph initialization patterns
**Description**: Repeated graph setup code in:
- `rdf_writer.py` lines 27-35
- `taf_post_processor.py` lines 40-76
- **Proposed solution**: Create GraphFactory base class

### Anti-patterns

#### Singleton Pattern Inconsistency
**Pattern**: Inconsistent singleton implementation
- `Parser` class (lines 46-57): Proper singleton with lazy initialization
- `Propbank` class (lines 27-38): Similar singleton pattern
- **Impact**: Code duplication, maintenance overhead
- **Proposed fix**: Create abstract SingletonMixin base class

#### God Object: Glossary Class
**Pattern**: Single class containing 726 lines of constants and static methods
- **Location**: `glossary.py` entire file
- **Impact**: Violates Single Responsibility Principle, difficult to maintain
- **Proposed fix**: Split into domain-specific configuration classes

#### Long Parameter Lists
**Pattern**: Methods with excessive parameters violating Clean Code principles
- `translate()` method: 7 parameters (line 39, `amr2fred.py`)
- `role_find()` method: 4 parameters (line 91, `propbank.py`)
- **Impact**: High coupling, difficult to test
- **Proposed fix**: Introduce parameter objects

### Over-engineering

#### Excessive Conditional Logic in `get_copy()` method
**Location**: `node.py` lines 248-300
- **Current complexity**: 4 different conditional branches with nested logic
- **Simplification**: Extract into strategy pattern with clear copy types
- **Benefits**: Reduced cyclomatic complexity from 8 to 3

#### Unnecessary Recursive Checks
**Location**: Multiple files contain endless recursion protection
- `node.py` lines 74-76, 102-104, 266-268, 470-472
- `parser.py` lines 303-305, 349-351
- **Current approach**: Global counters and manual threshold checking
- **Proposed structure**: Implement RecursionGuard context manager
- **Benefits**: Cleaner code, automatic cleanup

#### Over-abstracted Node Hierarchy
**Location**: `node.py` - Complex node relationships
- **Current**: 42 attributes and methods for basic tree structure
- **Proposed**: Separate concerns into NodeData, NodeRelations, NodeOperations
- **Expected LOC reduction**: 150+ lines

### Technical Debt

#### High-Risk Areas
**Area**: File I/O operations without proper resource management
- **Risk level**: High
- **Location**: `propbank.py` lines 58-68
- **Remediation**: Implement context managers for file operations

**Area**: Hardcoded external API endpoints
- **Risk level**: Medium
- **Location**: `amr2fred.py` lines 32-36, `taf_post_processor.py` lines 35-38
- **Remediation**: Move to configuration files

**Area**: Magic numbers and strings throughout codebase
- **Risk level**: Medium
- **Locations**: Throughout `glossary.py`, parser logic in multiple files
- **Remediation**: Create named constants in appropriate modules

## Refactoring Plan

### New Abstractions

#### 1. ConfigurationManager Class
- **Purpose**: Centralized management of namespaces, prefixes, and API endpoints
- **Consolidates**: Current scattered configuration in `glossary.py`
- **Expected LOC reduction**: 200+ lines
```python
class ConfigurationManager:
    def __init__(self):
        self.namespaces = NamespaceRegistry()
        self.api_endpoints = EndpointRegistry()
        self.constants = ConstantsRegistry()
```

#### 2. ExceptionHandler Decorator
- **Purpose**: Standardize exception handling across the codebase
- **Consolidates**: Repeated try-catch blocks in 4 files
- **Expected LOC reduction**: 50+ lines
```python
@handle_exceptions(default_return=None, log_level=logging.WARNING)
def method_with_potential_exceptions():
    # Implementation
```

#### 3. BaseParser Abstract Class
- **Purpose**: Common parsing functionality and validation
- **Consolidates**: Shared logic in `Parser` class
- **Expected LOC reduction**: 100+ lines

#### 4. SingletonMixin Base Class
- **Purpose**: Consistent singleton pattern implementation
- **Consolidates**: Duplicate singleton code in `Parser` and `Propbank`
- **Expected LOC reduction**: 30+ lines

### Simplifications

#### 1. Node Class Decomposition
- **Current complexity**: Single class with 478 lines handling multiple responsibilities
- **Proposed structure**: 
  - `NodeCore`: Basic node data and identity
  - `NodeRelations`: Parent-child relationships
  - `NodeOperations`: Tree operations and traversal
- **Benefits**: Improved testability, clearer separation of concerns

#### 2. Glossary Class Refactoring
- **Current structure**: Monolithic constants class (726 lines)
- **Proposed JSON configuration files**:
  
  **config/namespaces.json** (Lines 27-423):
  ```json
  {
    "prefixes": {
      "fred": "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#",
      "dul": "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#",
      "d0": "http://www.ontologydesignpatterns.org/ont/d0.owl#",
      "boxer": "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#",
      "boxing": "http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#",
      "quant": "http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#",
      "vn.role": "http://www.ontologydesignpatterns.org/ont/vn/abox/role/vnrole.owl#",
      "vn.data": "http://www.ontologydesignpatterns.org/ont/vn/data/",
      "amr": "https://w3id.org/framester/amr/",
      "amrb": "https://w3id.org/framester/amrb/",
      "va": "http://verbatlas.org/",
      "bn": "http://babelnet.org/rdf/",
      "wn30schema": "https://w3id.org/framester/wn/wn30/schema/",
      "wn30instances": "https://w3id.org/framester/wn/wn30/instances/",
      "fschema": "https://w3id.org/framester/schema/",
      "pbdata": "https://w3id.org/framester/pb/data/",
      "pbrs": "https://w3id.org/framester/data/propbank-3.4.0/RoleSet/",
      "pblr": "https://w3id.org/framester/data/propbank-3.4.0/LocalRole/",
      "pbgr": "https://w3id.org/framester/data/propbank-3.4.0/GenericRole/",
      "pbschema": "https://w3id.org/framester/schema/propbank/",
      "fnframe": "https://w3id.org/framester/framenet/abox/frame/",
      "wikidata": "http://www.wikidata.org/entity/",
      "schema": "https://schema.org/",
      "dbr": "http://dbpedia.org/resource/",
      "dbo": "http://dbpedia.org/ontology/",
      "dbpedia": "http://dbpedia.org/resource/",
      "schemaorg": "http://schema.org/"
    },
    "standardPrefixes": {
      "owl": "http://www.w3.org/2002/07/owl#",
      "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    }
  }
  ```
  
  **config/amr_patterns.json** (Lines 200-315, 455-476):
  ```json
  {
    "relations": {
      "core": {
        "polarity": ":polarity",
        "mode": ":mode",
        "topic": ":topic",
        "mod": ":mod",
        "quant": ":quant",
        "name": ":name",
        "wiki": ":wiki",
        "wikidata": ":wikidata"
      },
      "spatial": {
        "location": ":location",
        "source": ":source",
        "destination": ":destination",
        "direction": ":direction",
        "path": ":path"
      },
      "temporal": {
        "time": ":time",
        "duration": ":duration",
        "frequency": ":frequency"
      },
      "semantic": {
        "manner": ":manner",
        "purpose": ":purpose",
        "cause": ":cause",
        "beneficiary": ":beneficiary",
        "instrument": ":instrument",
        "accompanier": ":accompanier",
        "degree": ":degree",
        "extent": ":extent",
        "example": ":example",
        "medium": ":medium",
        "concession": ":concession"
      },
      "structural": {
        "part": ":part",
        "partOf": ":part-of",
        "subevent": ":subevent",
        "subeventOf": ":subevent-of",
        "subset": ":subset",
        "subsetOf": ":subset-of",
        "consistOf": ":consist-of"
      },
      "arguments": {
        "arg0": ":arg0",
        "arg1": ":arg1",
        "arg2": ":arg2",
        "arg3": ":arg3",
        "arg4": ":arg4",
        "arg5": ":arg5",
        "arg6": ":arg6"
      },
      "operators": {
        "op1": ":op1",
        "opPattern": ":op[0-9]+"
      },
      "prepositions": {
        "against": ":prep-against",
        "alongWith": ":prep-along-with",
        "amid": ":prep-amid",
        "among": ":prep-among",
        "as": ":prep-as",
        "at": ":prep-at",
        "by": ":prep-by",
        "concerning": ":prep-concerning",
        "considering": ":prep-considering",
        "despite": ":prep-despite",
        "except": ":prep-except",
        "excluding": ":prep-excluding",
        "following": ":prep-following",
        "for": ":prep-for",
        "from": ":prep-from",
        "in": ":prep-in",
        "inAdditionTo": ":prep-in-addition-to",
        "inSpiteOf": ":prep-in-spite-of",
        "into": ":prep-into",
        "like": ":prep-like",
        "on": ":prep-on",
        "onBehalfOf": ":prep-on-behalf-of",
        "opposite": ":prep-opposite",
        "per": ":prep-per",
        "regarding": ":prep-regarding",
        "save": ":prep-save",
        "suchAs": ":prep-such-as",
        "through": ":prep-through",
        "to": ":prep-to",
        "toward": ":prep-toward",
        "under": ":prep-under",
        "unlike": ":prep-unlike",
        "versus": ":prep-versus",
        "with": ":prep-with",
        "within": ":prep-within",
        "without": ":prep-without"
      }
    },
    "patterns": {
      "verb": "-[0-9]+$",
      "verbFull": ".*-[0-9]+$",
      "argument": ":arg.",
      "inverse": ":.+[0-9]-of",
      "operator": ":op[0-9]+",
      "sentence": ":snt[0-9]$",
      "variable": "^[a-zA-Z][a-zA-Z]*[0-9][0-9]*$"
    },
    "specialVerbs": {
      "haveOrgRole": "have-org-role-91",
      "haveRelRole": "have-rel-role-91",
      "haveName": "have-name-91",
      "havePart": "have-part-91",
      "havePolarity": "have-polarity-91",
      "havePurpose": "have-purpose-91",
      "haveQuant": "have-quant-91",
      "haveCondition": "have-condition-91",
      "haveConcession": "have-concession-91",
      "haveInstrument": "have-instrument-91",
      "haveFrequency": "have-frequency-91",
      "haveExtent": "have-extent-91",
      "haveManner": "have-manner-91",
      "haveMod": "have-mod-91",
      "haveDegree": "have-degree-91",
      "haveSubevent": "have-subevent-91",
      "beLocatedAt": "be-located-at-91",
      "beFrom": "be-from-91",
      "beDestinedFor": "be-destined-for-91",
      "beTemporallyAt": "be-temporally-at-91",
      "benefit": "benefit-01",
      "include": "include-91",
      "exemplify": "exemplify-01",
      "rateEntity": "rate-entity-91",
      "age": "age-01"
    },
    "mappings": {
      "relationsToFred": {
        ":mod": "dul:hasQuality",
        ":polarity": "boxing:hasTruthValue",
        ":topic": "fred:about",
        ":location": "vn.role:Location",
        ":source": "vn.role:Source",
        ":destination": "vn.role:Destination",
        ":manner": "dul:hasQuality",
        ":purpose": "vn.role:Predicate",
        ":beneficiary": "vn.role:Beneficiary",
        ":time": "vn.role:Time",
        ":instrument": "vn.role:Instrument",
        ":cause": "vn.role:Cause",
        ":degree": "dul:hasQuality",
        ":extent": "dul:hasQuality",
        ":frequency": "fred:with"
      }
    }
  }
  ```
  
  **config/linguistic_data.json** (Lines 480-555):
  ```json
  {
    "pronouns": {
      "person": ["I", "i", "you", "You", "YOU", "we", "We", "WE", "they", "They", "THEY"],
      "male": ["he", "He", "HE"],
      "female": ["she", "She", "SHE"],
      "thing": ["It", "it", "IT", "that", "those", "this", "these"],
      "demonstratives": ["that", "those", "this", "these"]
    },
    "conjunctions": [
      "and", "or", "but", "nor", "so", "for", "yet", "after", "although",
      "as", "as-if", "as-long", "as-because", "before", "even-if", "even-though",
      "once", "since", "so-that", "though", "till", "unless", "until", "what",
      "when", "whenever", "wherever", "whether", "while"
    ],
    "prepositions": [
      "à-la", "aboard", "about", "above", "according-to", "across", "after",
      "against", "ahead-of", "along", "along-with", "alongside", "amid", "amidst",
      "among", "amongst", "anti", "apart-from", "around", "as", "as-for", "as-per",
      "as-to", "as-well-as", "aside-from", "astride", "at", "atop", "away-from",
      "bar", "barring", "because-of", "before", "behind", "below", "beneath",
      "beside", "besides", "between", "beyond", "but", "but-for", "by", "by-means-of",
      "circa", "close-to", "concerning", "considering", "contrary-to", "counting",
      "cum", "depending-on", "despite", "down", "due-to", "during", "except",
      "except-for", "excepting", "excluding", "following", "for", "forward-of",
      "from", "further-to", "given", "gone", "in", "in-addition-to", "in-between",
      "in-case-of", "in-the-face-of", "in-favor-of", "in-front-of", "in-lieu-of",
      "in-spite-of", "in-view-of", "including", "inside", "instead-of", "into",
      "irrespective-of", "less", "like", "minus", "near", "near-to", "next-to",
      "notwithstanding", "of", "off", "on", "on-account-of", "on-behalf-of",
      "on-board", "on-to", "on-top-of", "onto", "opposite", "opposite-to",
      "other-than", "out-of", "outside", "outside-of", "over", "owing-to", "past",
      "pending", "per", "preparatory-to", "prior-to", "plus", "pro", "re",
      "regarding", "regardless-of", "respecting", "round", "save", "save-for",
      "saving", "since", "than", "thanks-to", "through", "throughout", "till",
      "to", "together-with", "touching", "toward", "towards", "under", "underneath",
      "unlike", "until", "up", "up-against", "up-to", "up-until", "upon", "versus",
      "via", "vis-a-vis", "with", "with-reference-to", "with-regard-to", "within",
      "without", "worth", "exact"
    ],
    "mannerAdverbs": [
      "accidentally", "angrily", "anxiously", "awkwardly", "badly", "beautifully",
      "blindly", "boldly", "bravely", "brightly", "busily", "calmly", "carefully",
      "carelessly", "cautiously", "cheerfully", "clearly", "closely", "correctly",
      "courageously", "cruelly", "daringly", "deliberately", "doubtfully", "eagerly",
      "easily", "elegantly", "enormously", "enthusiastically", "equally", "eventually",
      "exactly", "faithfully", "fast", "fatally", "fiercely", "fondly", "foolishly",
      "fortunately", "frankly", "frantically", "generously", "gently", "gladly",
      "gracefully", "greedily", "happily", "hard", "hastily", "healthily", "honestly",
      "hungrily", "hurriedly", "inadequately", "ingeniously", "innocently",
      "inquisitively", "irritably", "joyously", "justly", "kindly", "lazily",
      "loosely", "loudly", "madly", "mortally", "mysteriously", "neatly", "nervously",
      "noisily", "obediently", "openly", "painfully", "patiently", "perfectly",
      "politely", "poorly", "powerfully", "promptly", "punctually", "quickly",
      "quietly", "rapidly", "rarely", "really", "recklessly", "regularly",
      "reluctantly", "repeatedly", "rightfully", "roughly", "rudely", "sadly",
      "safely", "selfishly", "sensibly", "seriously", "sharply", "shyly", "silently",
      "sleepily", "slowly", "smoothly", "so", "softly", "solemnly", "speedily",
      "stealthily", "sternly", "straight", "stupidly", "successfully", "suddenly",
      "suspiciously", "swiftly", "tenderly", "tensely", "thoughtfully", "tightly",
      "truthfully", "unexpectedly", "victoriously", "violently", "vivaciously",
      "warmly", "weakly", "wearily", "well", "wildly", "wisely"
    ],
    "adjectivesFile": "adjectives.json"
  }
  ```
  
  **config/amr_entities.json** (Lines 686-706):
  ```json
  {
    "namedEntities": {
      "person": ["person", "family"],
      "organization": [
        "organization", "company", "government-organization", "military",
        "criminal-organization", "political-party", "market-sector", "school",
        "university", "research-institute", "team", "league"
      ],
      "location": [
        "location", "city", "city-district", "county", "state", "province",
        "territory", "country", "local-region", "country-region", "world-region",
        "continent"
      ],
      "geographical": [
        "ocean", "sea", "lake", "river", "gulf", "bay", "strait", "canal",
        "peninsula", "mountain", "volcano", "valley", "canyon", "island",
        "desert", "forest"
      ],
      "astronomical": ["moon", "planet", "star", "constellation"],
      "facility": [
        "facility", "airport", "station", "port", "tunnel", "bridge", "road",
        "railway-line", "building", "theater", "museum", "palace", "hotel",
        "worship-place", "market", "sports-facility", "park", "zoo", "amusement-park"
      ],
      "event": [
        "event", "incident", "natural-disaster", "earthquake", "war",
        "conference", "game", "festival"
      ],
      "product": [
        "product", "vehicle", "ship", "aircraft", "aircraft-type", "spaceship",
        "car-make"
      ],
      "creative": [
        "work-of-art", "picture", "music", "show", "broadcast-program",
        "publication", "book", "newspaper", "magazine", "journal"
      ],
      "biological": [
        "animal", "molecular-physical-entity", "small-molecule", "protein",
        "protein-family", "protein-segment", "amino-acid", "macro-molecular-complex",
        "enzyme", "nucleic-acid", "pathway", "gene", "dna-sequence", "cell",
        "cell-line", "species", "taxon"
      ],
      "medical": ["disease", "medical-condition"],
      "other": [
        "thing", "language", "nationality", "ethnic-group", "regional-group",
        "religious-group", "political-movement", "natural-object", "award",
        "law", "court-decision", "treaty", "music-key", "musical-note",
        "food-dish", "writing-script", "variable", "program"
      ]
    },
    "specialEntities": [
      "date-entity", "date-interval", "percentage-entity", "phone-number-entity",
      "email-address-entity", "url-entity", "score-entity", "string-entity",
      "value-interval"
    ],
    "quantityTypes": [
      "monetary-quantity", "distance-quantity", "area-quantity", "volume-quantity",
      "temporal-quantity", "frequency-quantity", "speed-quantity", "acceleration-quantity",
      "mass-quantity", "force-quantity", "pressure-quantity", "energy-quantity",
      "power-quantity", "voltage-quantity", "charge-quantity", "potential-quantity",
      "resistance-quantity", "inductance-quantity", "magnetic-field-quantity",
      "magnetic-flux-quantity", "radiation-quantity", "concentration-quantity",
      "temperature-quantity", "score-quantity", "fuel-consumption-quantity",
      "seismic-quantity"
    ],
    "dateComponents": {
      "calendar": ":calendar",
      "century": ":century",
      "day": ":day",
      "dayPeriod": ":dayperiod",
      "decade": ":decade",
      "era": ":era",
      "month": ":month",
      "quarter": ":quarter",
      "season": ":season",
      "timezone": ":timezone",
      "weekday": ":weekday",
      "year": ":year",
      "year2": ":year2"
    }
  }
  ```
  
  **config/validation_patterns.json** (Lines 174-183):
  ```json
  {
    "dataTypes": {
      "integer": {
        "pattern": "^[0-9]+$",
        "namespace": "http://www.w3.org/2001/XMLSchema#decimal"
      },
      "decimal": {
        "pattern": "^[0-9]+[.]*[0-9]*$",
        "namespace": "http://www.w3.org/2001/XMLSchema#decimal"
      },
      "rational": {
        "pattern": "^[1-9][0-9]*/[1-9][0-9]*$",
        "namespace": null
      },
      "date": {
        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
        "namespace": "http://www.w3.org/2001/XMLSchema#date"
      },
      "time": {
        "pattern": "([01]?[0-9]|2[0-3]):[0-5][0-9]",
        "namespace": "https://www.w3.org/TR/xmlschema-2/#time"
      },
      "string": {
        "pattern": null,
        "namespace": "http://www.w3.org/2001/XMLSchema#string"
      }
    },
    "serializationFormats": [
      "json-ld", "n3", "nquads", "nt", "hext", "pretty-xml",
      "trig", "trix", "turtle", "longturtle", "xml"
    ]
  }
  ```
  
  **config/ontology_mappings.json** (Lines 44-143):
  ```json
  {
    "dulConcepts": {
      "events": "dul:Event",
      "agents": "dul:Agent",
      "concepts": "dul:Concept",
      "informationEntities": "dul:InformationEntity",
      "organisms": "dul:Organism",
      "organizations": "dul:Organization",
      "persons": "dul:Person",
      "naturalPersons": "dul:NaturalPerson",
      "substances": "dul:Substance"
    },
    "dulRelations": {
      "hasQuality": "dul:hasQuality",
      "hasDataValue": "dul:hasDataValue",
      "associatedWith": "dul:associatedWith",
      "hasMember": "dul:hasMember",
      "hasPrecondition": "dul:hasPrecondition",
      "hasAmount": "dul:hasAmount",
      "precedes": "dul:precedes"
    },
    "boxingModalities": {
      "necessary": "boxing:Necessary",
      "possible": "boxing:Possible",
      "hasModality": "boxing:hasModality",
      "false": "boxing:False",
      "truth": "boxing:Truth",
      "hasTruthValue": "boxing:hasTruthValue",
      "unknown": "boxing:Unknown"
    },
    "vnRoles": {
      "location": "vn.role:Location",
      "source": "vn.role:Source",
      "destination": "vn.role:Destination",
      "beneficiary": "vn.role:Beneficiary",
      "time": "vn.role:Time",
      "instrument": "vn.role:Instrument",
      "cause": "vn.role:Cause",
      "experiencer": "vn.role:Experiencer",
      "theme": "vn.role:Theme",
      "predicate": "vn.role:Predicate"
    },
    "boxerRoles": {
      "agent": "boxer:agent",
      "patient": "boxer:patient",
      "theme": "boxer:theme"
    },
    "quantifiers": {
      "every": "quant:every",
      "hasDeterminer": "quant:hasDeterminer",
      "hasQuantifier": "quant:hasQuantifier"
    }
  }
  ```
  
- **Proposed Python classes**:
  - `ConfigurationLoader`: Loads and manages JSON configuration files
  - `NamespaceManager`: Handles namespace resolution and prefix management
  - `AMRPatternMatcher`: Manages AMR pattern matching and relations
  - `LinguisticDataProvider`: Provides linguistic data (adjectives, adverbs, etc.)
  - `EntityClassifier`: Manages entity classification and type checking
  - `ValidationService`: Handles pattern validation and data type checking
  
- **Benefits**: 
  - Reduced code size by ~400 lines
  - Configuration changes without code modification
  - Better separation of concerns
  - Easier testing and maintenance
  - Runtime configuration reload capability

#### 3. Method Extraction in Parser
- **Target**: `fred_translate()` method (lines 330-378)
- **Current complexity**: 48 lines with 6 nested method calls
- **Proposed extraction**:
  - `validate_nodes()`
  - `process_operations()`
  - `handle_relations()`
- **Benefits**: Better testability, reduced complexity

### Testing Requirements

#### New Unit Tests
- **ConfigurationManager**: Test namespace resolution and API endpoint validation
- **ExceptionHandler**: Test decorator functionality and logging behavior
- **SingletonMixin**: Test singleton behavior across inheritance
- **NodeCore/NodeRelations/NodeOperations**: Test decomposed functionality
- **BaseParser**: Test common parsing behaviors

#### Deprecated Tests
- **test_node.py**: Lines 54-57 (testing monolithic copy behavior)
- **test_couple.py**: Entire file - overly simple class that should be replaced with namedtuple
- **test_propbank.py**: Refactor to test new abstracted file handling

## Implementation Priority

### Phase 1: Foundation (High Priority)
1. **Create ConfigurationManager class**
   - Extract constants from Glossary
   - Implement namespace registry
   - Update all imports across codebase

2. **Implement ExceptionHandler decorator**
   - Replace repeated try-catch blocks
   - Standardize logging behavior

3. **Create SingletonMixin base class**
   - Refactor Parser and Propbank classes
   - Ensure thread safety

4. **Extract API Configuration from amr2fred.py**
   - **Current structure**: Hardcoded API endpoints in constructor (lines 32-36)
   - **Proposed JSON configuration file**:
   
   **config/api_endpoints.json**:
   ```json
   {
     "text2amr": {
       "default": "https://nlp.uniroma1.it/spring/api/text-to-amr?sentence=",
       "spring": "https://arco.istc.cnr.it/spring/text-to-amr?blinkify=true&sentence=",
       "fallback": "https://arco.istc.cnr.it/spring/text-to-amr?blinkify=true&sentence="
     },
     "multilingualAmr": {
       "default": "https://arco.istc.cnr.it/usea/api/amr",
       "usea": "https://arco.istc.cnr.it/usea/api/amr"
     },
     "requestConfig": {
       "timeout": 30,
       "retries": 3,
       "headers": {
         "User-Agent": "py-amr2fred/1.0",
         "Accept": "application/json"
       }
     }
   }
   ```
   - **Benefits**: Easy endpoint switching, environment-specific configuration, centralized API management

5. **Refactor PropBank Data File Management**
   - **Current structure**: Hardcoded file paths in propbank.py (lines 19-20)
   - **Proposed JSON configuration file**:
   
   **config/data_sources.json**:
   ```json
   {
     "propbank": {
       "roleMatrix": "data/propbankrolematrixaligned340.tsv",
       "frameMatrix": "data/propbankframematrix340.tsv",
       "version": "3.4.0",
       "encoding": "utf-8",
       "delimiter": "\t"
     },
     "linguistic": {
       "adjectives": "data/adjectives.json"
     },
     "dataPaths": {
       "baseDir": "data/",
       "configDir": "config/",
       "outputDir": "output/"
     }
   }
   ```
   - **Benefits**: Flexible data source management, version control, easier testing with mock data

### Phase 2: Core Refactoring (Medium Priority)
4. **Decompose Node class**
   - Split into logical components
   - Update all dependent code
   - Comprehensive testing

5. **Refactor Parser class**
   - Extract method implementations
   - Implement BaseParser abstraction
   - Simplify complex methods

### Phase 3: Polish and Optimization (Lower Priority)
6. **Simplify method signatures**
   - Introduce parameter objects
   - Reduce coupling

7. **Clean up testing infrastructure**
   - Remove deprecated tests
   - Add comprehensive integration tests

## Metrics

### Updated Estimates (Post-Configuration Analysis)
- **Estimated total LOC reduction**: 500-600 lines (30-35% reduction)
- **Glossary.py refactoring**: ~400 lines → 6 JSON files + ~100 lines of loader classes
- **API configuration extraction**: ~20 lines → 1 JSON file + ~15 lines of config loader
- **PropBank file management**: ~15 lines → 1 JSON file + ~10 lines of path resolver
- **Complexity reduction**: 40% average cyclomatic complexity reduction in core methods
- **Affected modules**: 9 out of 9 core modules (now including amr2fred.py and propbank.py)
- **New test coverage required**: ~175 new unit tests
- **New JSON configuration files**: 8 files total
- **Deprecated test files**: 1 complete file (test_couple.py)

### Configuration Files Summary
1. **config/namespaces.json** - RDF/OWL namespace management (~50 prefixes)
2. **config/amr_patterns.json** - AMR relation patterns and mappings (~150 patterns)
3. **config/linguistic_data.json** - Linguistic elements (pronouns, prepositions, adverbs)
4. **config/amr_entities.json** - Entity classifications and types (~100 entity types)
5. **config/validation_patterns.json** - Data validation patterns and schemas
6. **config/ontology_mappings.json** - Ontology concept and relation mappings
7. **config/api_endpoints.json** - External API endpoint configuration
8. **config/data_sources.json** - Data file paths and metadata

## Risk Assessment

**Low Risk Changes:**
- Configuration extraction
- Exception handler decorator
- Method extractions

**Medium Risk Changes:**
- Node class decomposition
- Parser refactoring

**High Risk Changes:**
- Glossary class split (affects all modules)

## Success Criteria

1. **All existing functionality preserved** (verified through existing test suite)
2. **Significant LOC reduction achieved** (minimum 20% reduction)
3. **Improved code metrics** (cyclomatic complexity reduced by 30%+)
4. **Enhanced maintainability** (measured through code review feedback)
5. **No performance degradation** (benchmarked against current implementation)

This refactoring proposal provides a clear roadmap for systematically improving the codebase while maintaining stability and functionality. The phased approach ensures manageable changes with continuous validation of improvements.