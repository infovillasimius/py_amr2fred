import json
import logging
from enum import Enum
from typing import List, Dict, Any, Optional

from .config_manager import ConfigurationManager

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class classproperty:
    """Descriptor for class-level properties."""
    def __init__(self, func):
        self.func = func
        
    def __get__(self, obj, cls):
        return self.func(cls)


class GlossaryMeta(type):
    """Metaclass to enable class-level property access for backward compatibility."""
    
    def __getattribute__(cls, name):
        # First check if it's a special method or class-level constant
        if name.startswith('_') or name in ['TOP', 'INSTANCE', 'ENDLESS', 'ENDLESS2', 'RECURSIVE_ERROR']:
            return super().__getattribute__(name)
            
        # Check for enum classes
        if name in ['RdflibMode', 'NodeType', 'NodeStatus', 'PropbankFrameFields', 'PropbankRoleFields']:
            return super().__getattribute__(name)
        
        # Check if it's a method
        try:
            attr = super().__getattribute__(name)
            if callable(attr) and not isinstance(attr, property):
                return attr
        except AttributeError:
            pass
        
        # For properties and other attributes, delegate to singleton instance
        try:
            instance = get_glossary_instance()
            if hasattr(instance, name):
                return getattr(instance, name)
        except:
            # Fallback to normal attribute access
            pass
            
        # Fallback to normal class attribute access
        return super().__getattribute__(name)


class Glossary(metaclass=GlossaryMeta):
    """
    A collection of constants and predefined terms used throughout the py_amr2fred library.

    This class provides ontology namespaces, prefixes, error messages, and various configuration
    values needed for RDF generation, parsing, and semantic processing. It serves as a central
    reference for terminology used in the system.
    
    This refactored version uses ConfigurationManager for centralized configuration management.
    """
    
    # Singleton instance for backward compatibility
    _instance: Optional['Glossary'] = None
    
    def __init__(self):
        """Initialize Glossary with ConfigurationManager."""
        self._config = ConfigurationManager.get_instance()
    
    @classmethod
    def get_instance(cls) -> 'Glossary':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    @property
    def config(self) -> ConfigurationManager:
        """Get the configuration manager instance."""
        return self._config
        
    # Core constants that don't need configuration management
    ENDLESS = 1000
    ENDLESS2 = 800
    RECURSIVE_ERROR = " recursive error! "
    TOP = "top"
    INSTANCE = "instance"

    # Namespace and prefix properties using ConfigurationManager
    @property
    def FRED_NS(self) -> str:
        """Get FRED namespace."""
        return self._config.namespaces.get_namespace('fred') or "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"
    
    @FRED_NS.setter
    def FRED_NS(self, value: str) -> None:
        """Set FRED namespace dynamically."""
        self._config.namespaces.set_namespace('fred', value)
    
    @property
    def DEFAULT_FRED_NS(self) -> str:
        """Get default FRED namespace."""
        return self.FRED_NS
        
    @property
    def FRED(self) -> str:
        """Get FRED prefix."""
        return "fred:"
        
    # Core FRED properties
    @property
    def FRED_TOPIC(self) -> str:
        return f"{self.FRED}Topic"
        
    @property
    def FRED_ABOUT(self) -> str:
        return f"{self.FRED}about"

    # DUL namespace properties
    @property
    def DUL_NS(self) -> str:
        """Get DUL namespace."""
        return self._config.namespaces.get_namespace('dul') or "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"
    
    @property
    def DUL(self) -> str:
        """Get DUL prefix."""
        return "dul:"
        
    # D0 namespace properties  
    @property
    def D0_NS(self) -> str:
        """Get D0 namespace."""
        return self._config.namespaces.get_namespace('d0') or "http://www.ontologydesignpatterns.org/ont/d0.owl#"
    
    @property
    def D0(self) -> str:
        """Get D0 prefix."""
        return "d0:"

    # DUL properties
    @property
    def DUL_EVENT(self) -> str:
        return f"{self.DUL}Event"
        
    @property
    def DUL_HAS_QUALITY(self) -> str:
        return f"{self.DUL}hasQuality"
        
    @property
    def DUL_HAS_DATA_VALUE(self) -> str:
        return f"{self.DUL}hasDataValue"
        
    @property
    def DUL_ASSOCIATED_WITH(self) -> str:
        return f"{self.DUL}associatedWith"
        
    @property
    def DUL_HAS_MEMBER(self) -> str:
        return f"{self.DUL}hasMember"
        
    @property
    def DUL_HAS_PRECONDITION(self) -> str:
        return f"{self.DUL}hasPrecondition"
        
    @property
    def DUL_HAS_AMOUNT(self) -> str:
        return f"{self.DUL}hasAmount"
        
    @property
    def DUL_PRECEDES(self) -> str:
        return f"{self.DUL}precedes"

    # DUL entity types
    @property
    def DUL_AGENT(self) -> str:
        return f"{self.DUL}Agent"
        
    @property
    def DUL_CONCEPT(self) -> str:
        return f"{self.DUL}Concept"
        
    @property
    def DUL_INFORMATION_ENTITY(self) -> str:
        return f"{self.DUL}InformationEntity"
        
    @property
    def DUL_ORGANISM(self) -> str:
        return f"{self.DUL}Organism"
        
    @property
    def DUL_ORGANIZATION(self) -> str:
        return f"{self.DUL}Organization"
        
    @property
    def DUL_PERSON(self) -> str:
        return f"{self.DUL}Person"
        
    @property
    def DUL_NATURAL_PERSON(self) -> str:
        return f"{self.DUL}NaturalPerson"
        
    @property
    def DUL_SUBSTANCE(self) -> str:
        return f"{self.DUL}Substance"

    # D0 properties
    @property
    def D0_LOCATION(self) -> str:
        return f"{self.D0}Location"
        
    @property
    def D0_TOPIC(self) -> str:
        return f"{self.D0}Topic"

    # DUL collections
    @property
    def DULS(self) -> List[str]:
        return [
            self.DUL_AGENT, self.DUL_CONCEPT, self.DUL_INFORMATION_ENTITY, 
            self.DUL_ORGANISM, self.DUL_ORGANIZATION, self.DUL_SUBSTANCE, 
            self.D0_TOPIC, self.D0_LOCATION, self.DUL_PERSON
        ]
        
    @property
    def DULS_CHECK(self) -> List[str]:
        return ["agent", "concept", "informationentity", "organism", "organization", 
                "substance", "topic", "location", "person"]

    # Boxer namespace properties
    @property
    def BOXER_NS(self) -> str:
        """Get Boxer namespace."""
        return self._config.namespaces.get_namespace('boxer') or "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#"
    
    @property
    def BOXER(self) -> str:
        """Get Boxer prefix."""
        return "boxer:"
        
    @property
    def BOXER_AGENT(self) -> str:
        return f"{self.BOXER}agent"
        
    @property
    def BOXER_PATIENT(self) -> str:
        return f"{self.BOXER}patient"
        
    @property
    def BOXER_THEME(self) -> str:
        return f"{self.BOXER}theme"

    # Boxing namespace properties
    @property
    def BOXING_NS(self) -> str:
        """Get Boxing namespace."""
        return self._config.namespaces.get_namespace('boxing') or "http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#"
    
    @property
    def BOXING(self) -> str:
        """Get Boxing prefix."""
        return "boxing:"
        
    @property
    def BOXING_NECESSARY(self) -> str:
        return f"{self.BOXING}Necessary"
        
    @property
    def BOXING_POSSIBLE(self) -> str:
        return f"{self.BOXING}Possible"
        
    @property
    def BOXING_HAS_MODALITY(self) -> str:
        return f"{self.BOXING}hasModality"
        
    @property
    def BOXING_FALSE(self) -> str:
        return f"{self.BOXING}False"
        
    @property
    def BOXING_TRUTH(self) -> str:
        return f"{self.BOXING}Truth"
        
    @property
    def BOXING_HAS_TRUTH_VALUE(self) -> str:
        return f"{self.BOXING}hasTruthValue"
        
    @property
    def BOXING_UNKNOWN(self) -> str:
        return f"{self.BOXING}Unknown"

    # Quant namespace properties
    @property
    def QUANT_NS(self) -> str:
        """Get Quant namespace."""
        return self._config.namespaces.get_namespace('quant') or "http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"
    
    @property
    def QUANT(self) -> str:
        """Get Quant prefix."""
        return "quant:"
        
    @property
    def QUANT_EVERY(self) -> str:
        return f"{self.QUANT}every"
        
    @property
    def QUANT_HAS_DETERMINER(self) -> str:
        return f"{self.QUANT}hasDeterminer"
        
    @property
    def QUANT_HAS_QUANTIFIER(self) -> str:
        return f"{self.QUANT}hasQuantifier"

    # Standard namespaces
    @property
    def OWL_NS(self) -> str:
        """Get OWL namespace."""
        return self._config.namespaces.get_namespace('owl') or "http://www.w3.org/2002/07/owl#"
    
    @property
    def OWL(self) -> str:
        """Get OWL prefix."""
        return "owl:"
        
    @property
    def OWL_THING(self) -> str:
        return f"{self.OWL}Thing"
        
    @property
    def OWL_EQUIVALENT_CLASS(self) -> str:
        return f"{self.OWL}equivalentClass"
        
    @property
    def OWL_SAME_AS(self) -> str:
        return f"{self.OWL}sameAs"
        
    @property
    def OWL_OBJECT_PROPERTY(self) -> str:
        return f"{self.OWL}ObjectProperty"
        
    @property
    def OWL_INVERSE_OF(self) -> str:
        return f"{self.OWL}inverseOf"
        
    @property
    def OWL_EQUIVALENT_PROPERTY(self) -> str:
        return f"{self.OWL}equivalentProperty"
        
    @property
    def OWL_DATA_TYPE_PROPERTY(self) -> str:
        return f"{self.OWL}DatatypeProperty"

    # RDF namespace properties
    @property
    def RDF_NS(self) -> str:
        """Get RDF namespace."""
        return self._config.namespaces.get_namespace('rdf') or "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    
    @property
    def RDF(self) -> str:
        """Get RDF prefix."""
        return "rdf:"
        
    @property
    def RDF_TYPE(self) -> str:
        return f"{self.RDF}type"

    # RDFS namespace properties
    @property
    def RDFS_NS(self) -> str:
        """Get RDFS namespace."""
        return self._config.namespaces.get_namespace('rdfs') or "http://www.w3.org/2000/01/rdf-schema#"
    
    @property
    def RDFS(self) -> str:
        """Get RDFS prefix."""
        return "rdfs:"
        
    @property
    def RDFS_SUBCLASS_OF(self) -> str:
        return f"{self.RDFS}subClassOf"
        
    @property
    def RDFS_SUB_PROPERTY_OF(self) -> str:
        return f"{self.RDFS}subPropertyOf"
        
    @property
    def RDFS_LABEL(self) -> str:
        return f"{self.RDFS}label"

    # VN Role namespace properties
    @property
    def VN_ROLE_NS(self) -> str:
        """Get VN Role namespace."""
        return self._config.namespaces.get_namespace('vn.role') or "http://www.ontologydesignpatterns.org/ont/vn/abox/role/vnrole.owl#"
    
    @property
    def VN_ROLE(self) -> str:
        """Get VN Role prefix."""
        return "vn.role:"
        
    @property
    def VN_ROLE_LOCATION(self) -> str:
        return f"{self.VN_ROLE}Location"
        
    @property
    def VN_ROLE_SOURCE(self) -> str:
        return f"{self.VN_ROLE}Source"
        
    @property
    def VN_ROLE_DESTINATION(self) -> str:
        return f"{self.VN_ROLE}Destination"
        
    @property
    def VN_ROLE_BENEFICIARY(self) -> str:
        return f"{self.VN_ROLE}Beneficiary"
        
    @property
    def VN_ROLE_TIME(self) -> str:
        return f"{self.VN_ROLE}Time"
        
    @property
    def VN_ROLE_INSTRUMENT(self) -> str:
        return f"{self.VN_ROLE}Instrument"
        
    @property
    def VN_ROLE_CAUSE(self) -> str:
        return f"{self.VN_ROLE}Cause"
        
    @property
    def VN_ROLE_EXPERIENCER(self) -> str:
        return f"{self.VN_ROLE}Experiencer"
        
    @property
    def VN_ROLE_THEME(self) -> str:
        return f"{self.VN_ROLE}Theme"
        
    @property
    def VN_ROLE_PREDICATE(self) -> str:
        return f"{self.VN_ROLE}Predicate"

    # AMR relations using pattern matcher
    @property
    def AMR_POLARITY(self) -> str:
        return self._config.patterns.get_relation('core', 'polarity') or ":polarity"
        
    @property
    def AMR_POLARITY_OF(self) -> str:
        return ":polarity-of"
        
    @property
    def AMR_MINUS(self) -> str:
        return self._config.patterns.get_constant('polarityValues.minus') or "-"
        
    @property
    def AMR_PLUS(self) -> str:
        return self._config.patterns.get_constant('polarityValues.plus') or "+"
        
    @property
    def AMR_MODE(self) -> str:
        return self._config.patterns.get_relation('core', 'mode') or ":mode"
        
    @property
    def AMR_POSS(self) -> str:
        return self._config.patterns.get_relation('core', 'poss') or ":poss"
        
    @property
    def AMR_ARG0(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg0') or ":arg0"
        
    @property
    def AMR_ARG1(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg1') or ":arg1"
        
    @property
    def AMR_ARG2(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg2') or ":arg2"
        
    @property
    def AMR_ARG3(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg3') or ":arg3"
        
    @property
    def AMR_ARG4(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg4') or ":arg4"
        
    @property
    def AMR_ARG5(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg5') or ":arg5"
        
    @property
    def AMR_ARG6(self) -> str:
        return self._config.patterns.get_relation('arguments', 'arg6') or ":arg6"
        
    @property
    def AMR_OP1(self) -> str:
        return self._config.patterns.get_relation('operators', 'op1') or ":op1"
        
    @property
    def AMR_QUANT(self) -> str:
        return self._config.patterns.get_relation('core', 'quant') or ":quant"
        
    @property
    def AMR_TOPIC(self) -> str:
        return self._config.patterns.get_relation('core', 'topic') or ":topic"
        
    @property
    def AMR_UNKNOWN(self) -> str:
        return self._config.patterns.get_constant('amrUnknown') or "amr-unknown"
        
    @property
    def AMR_MOD(self) -> str:
        return self._config.patterns.get_relation('core', 'mod') or ":mod"
        
    @property
    def AMR_LOCATION(self) -> str:
        return self._config.patterns.get_relation('spatial', 'location') or ":location"
        
    @property
    def AMR_SOURCE(self) -> str:
        return self._config.patterns.get_relation('spatial', 'source') or ":source"
        
    @property
    def AMR_DESTINATION(self) -> str:
        return self._config.patterns.get_relation('spatial', 'destination') or ":destination"
        
    @property
    def AMR_DIRECTION(self) -> str:
        return self._config.patterns.get_relation('spatial', 'direction') or ":direction"
        
    @property
    def AMR_PATH(self) -> str:
        return self._config.patterns.get_relation('spatial', 'path') or ":path"
        
    @property
    def AMR_MANNER(self) -> str:
        return self._config.patterns.get_relation('semantic', 'manner') or ":manner"
        
    @property
    def AMR_WIKI(self) -> str:
        return self._config.patterns.get_relation('core', 'wiki') or ":wiki"
        
    @property
    def AMR_NAME(self) -> str:
        return self._config.patterns.get_relation('core', 'name') or ":name"
        
    @property
    def AMR_PURPOSE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'purpose') or ":purpose"
        
    @property
    def AMR_POLITE(self) -> str:
        return ":polite"

    # Additional AMR relations
    @property
    def AMR_ACCOMPANIER(self) -> str:
        return self._config.patterns.get_relation('semantic', 'accompanier') or ":accompanier"
        
    @property
    def AMR_AGE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'age') or ":age"
        
    @property
    def AMR_BENEFICIARY(self) -> str:
        return self._config.patterns.get_relation('semantic', 'beneficiary') or ":beneficiary"
        
    @property
    def AMR_CAUSE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'cause') or ":cause"
        
    @property
    def AMR_COMPARED_TO(self) -> str:
        return self._config.patterns.get_relation('semantic', 'comparedTo') or ":compared-to"
        
    @property
    def AMR_CONCESSION(self) -> str:
        return self._config.patterns.get_relation('semantic', 'concession') or ":concession"
        
    @property
    def AMR_CONDITION(self) -> str:
        return self._config.patterns.get_relation('semantic', 'condition') or ":condition"
        
    @property
    def AMR_CONSIST_OF(self) -> str:
        return self._config.patterns.get_relation('structural', 'consistOf') or ":consist-of"
        
    @property
    def AMR_DEGREE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'degree') or ":degree"
        
    @property
    def AMR_DURATION(self) -> str:
        return self._config.patterns.get_relation('temporal', 'duration') or ":duration"
        
    @property
    def AMR_EXAMPLE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'example') or ":example"
        
    @property
    def AMR_EXTENT(self) -> str:
        return self._config.patterns.get_relation('semantic', 'extent') or ":extent"
        
    @property
    def AMR_FREQUENCY(self) -> str:
        return self._config.patterns.get_relation('temporal', 'frequency') or ":frequency"
        
    @property
    def AMR_INSTRUMENT(self) -> str:
        return self._config.patterns.get_relation('semantic', 'instrument') or ":instrument"
        
    @property
    def AMR_LI(self) -> str:
        return self._config.patterns.get_relation('semantic', 'li') or ":li"
        
    @property
    def AMR_MEDIUM(self) -> str:
        return self._config.patterns.get_relation('semantic', 'medium') or ":medium"
        
    @property
    def AMR_ORD(self) -> str:
        return self._config.patterns.get_relation('semantic', 'ord') or ":ord"
        
    @property
    def AMR_PART(self) -> str:
        return self._config.patterns.get_relation('structural', 'part') or ":part"
        
    @property
    def AMR_PART_OF(self) -> str:
        return self._config.patterns.get_relation('structural', 'partOf') or ":part-of"
        
    @property
    def AMR_QUANT_OF(self) -> str:
        return ":quant-of"
        
    @property
    def AMR_RANGE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'range') or ":range"
        
    @property
    def AMR_SCALE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'scale') or ":scale"
        
    @property
    def AMR_SUB_EVENT(self) -> str:
        return self._config.patterns.get_relation('structural', 'subevent') or ":subevent"
        
    @property
    def AMR_SUB_EVENT_OF(self) -> str:
        return self._config.patterns.get_relation('structural', 'subeventOf') or ":subevent-of"
        
    @property
    def AMR_SUBSET(self) -> str:
        return self._config.patterns.get_relation('structural', 'subset') or ":subset"
        
    @property
    def AMR_SUBSET_OF(self) -> str:
        return self._config.patterns.get_relation('structural', 'subsetOf') or ":subset-of"
        
    @property
    def AMR_TIME(self) -> str:
        return self._config.patterns.get_relation('temporal', 'time') or ":time"
        
    @property
    def AMR_UNIT(self) -> str:
        return self._config.patterns.get_relation('semantic', 'unit') or ":unit"
        
    @property
    def AMR_VALUE(self) -> str:
        return self._config.patterns.get_relation('semantic', 'value') or ":value"

    # Reification verbs from configuration
    @property
    def REIFI_BENEFIT(self) -> str:
        return self._config.patterns.get_special_verb('benefit') or "benefit-01"
        
    @property
    def REIFI_HAVE_CONCESSION(self) -> str:
        return self._config.patterns.get_special_verb('haveConcession') or "have-concession-91"
        
    @property
    def REIFI_HAVE_CONDITION(self) -> str:
        return self._config.patterns.get_special_verb('haveCondition') or "have-condition-91"
        
    @property
    def REIFI_BE_DESTINED_FOR(self) -> str:
        return self._config.patterns.get_special_verb('beDestinedFor') or "be-destined-for-91"
        
    @property
    def REIFI_EXEMPLIFY(self) -> str:
        return self._config.patterns.get_special_verb('exemplify') or "exemplify-01"
        
    @property
    def REIFI_HAVE_EXTENT(self) -> str:
        return self._config.patterns.get_special_verb('haveExtent') or "have-extent-91"
        
    @property
    def REIFI_HAVE_FREQUENCY(self) -> str:
        return self._config.patterns.get_special_verb('haveFrequency') or "have-frequency-91"
        
    @property
    def REIFI_HAVE_INSTRUMENT(self) -> str:
        return self._config.patterns.get_special_verb('haveInstrument') or "have-instrument-91"
        
    @property
    def REIFI_BE_LOCATED_AT(self) -> str:
        return self._config.patterns.get_special_verb('beLocatedAt') or "be-located-at-91"
        
    @property
    def REIFI_HAVE_MANNER(self) -> str:
        return self._config.patterns.get_special_verb('haveManner') or "have-manner-91"
        
    @property
    def REIFI_HAVE_MOD(self) -> str:
        return self._config.patterns.get_special_verb('haveMod') or "have-mod-91"
        
    @property
    def REIFI_HAVE_NAME(self) -> str:
        return self._config.patterns.get_special_verb('haveName') or "have-name-91"
        
    @property
    def REIFI_HAVE_PART(self) -> str:
        return self._config.patterns.get_special_verb('havePart') or "have-part-91"
        
    @property
    def REIFI_HAVE_POLARITY(self) -> str:
        return self._config.patterns.get_special_verb('havePolarity') or "have-polarity-91"
        
    @property
    def REIFI_HAVE_PURPOSE(self) -> str:
        return self._config.patterns.get_special_verb('havePurpose') or "have-purpose-91"
        
    @property
    def REIFI_HAVE_QUANT(self) -> str:
        return self._config.patterns.get_special_verb('haveQuant') or "have-quant-91"
        
    @property
    def REIFI_BE_FROM(self) -> str:
        return self._config.patterns.get_special_verb('beFrom') or "be-from-91"
        
    @property
    def REIFI_HAVE_SUBEVENT(self) -> str:
        return self._config.patterns.get_special_verb('haveSubevent') or "have-subevent-91"
        
    @property
    def REIFI_INCLUDE(self) -> str:
        return self._config.patterns.get_special_verb('include') or "include-91"
        
    @property
    def REIFI_BE_TEMPORALLY_AT(self) -> str:
        return self._config.patterns.get_special_verb('beTemporallyAt') or "be-temporally-at-91"
        
    @property
    def REIFI_HAVE_DEGREE(self) -> str:
        return self._config.patterns.get_special_verb('haveDegree') or "have-degree-91"
        
    @property
    def REIFI_HAVE_LI(self) -> str:
        return "have-li-91"
        
    @property
    def RATE_ENTITY(self) -> str:
        return self._config.patterns.get_special_verb('rateEntity') or "rate-entity-91"

    # VN Data namespace
    @property
    def VN_DATA_NS(self) -> str:
        """Get VN Data namespace."""
        return self._config.namespaces.get_namespace('vn.data') or "http://www.ontologydesignpatterns.org/ont/vn/data/"
    
    @property
    def VN_DATA(self) -> str:
        """Get VN Data prefix."""
        return "vn.data:"

    # Data type schemas using validation service
    @property
    def NN_INTEGER_NS(self) -> str:
        return "http://www.w3.org/2001/XMLSchema#decimal"
        
    @property
    def NN_INTEGER(self) -> str:
        return self._config.validation.get_data_type_info('integer')['pattern'] if self._config.validation.get_data_type_info('integer') else "^[0-9]+$"
        
    @property
    def NN_INTEGER2(self) -> str:
        return "^[0-9]+[.]*[0-9]*$"
        
    @property
    def NN_RATIONAL(self) -> str:
        return "^[1-9][0-9]*/[1-9][0-9]*$"

    @property
    def DATE_SCHEMA_NS(self) -> str:
        return "http://www.w3.org/2001/XMLSchema#date"
        
    @property
    def DATE_SCHEMA(self) -> str:
        return self._config.validation.get_data_type_info('date')['pattern'] if self._config.validation.get_data_type_info('date') else "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"

    @property
    def TIME_SCHEMA2_NS(self) -> str:
        return "https://www.w3.org/TR/xmlschema-2/#time"
        
    @property
    def TIME_SCHEMA2(self) -> str:
        return "time:"
        
    @property
    def TIME_SCHEMA(self) -> str:
        return "([01]?[0-9]|2[0-3]):[0-5][0-9]"

    @property
    def STRING_SCHEMA_NS(self) -> str:
        return "http://www.w3.org/2001/XMLSchema#string"

    # External ontologies
    @property
    def DBR_NS(self) -> str:
        """Get DBPedia Resource namespace."""
        return self._config.namespaces.get_namespace('dbr') or "http://dbpedia.org/resource/"
    
    @property
    def DBR(self) -> str:
        """Get DBPedia Resource prefix."""
        return "dbr:"

    @property
    def DBO_NS(self) -> str:
        """Get DBPedia Ontology namespace."""
        return self._config.namespaces.get_namespace('dbo') or "http://dbpedia.org/ontology/"
    
    @property
    def DBO(self) -> str:
        """Get DBPedia Ontology prefix."""
        return "dbo:"

    @property
    def DBPEDIA_NS(self) -> str:
        """Get DBPedia namespace."""
        return self._config.namespaces.get_namespace('dbpedia') or "http://dbpedia.org/resource/"
    
    @property
    def DBPEDIA(self) -> str:
        """Get DBPedia prefix."""
        return "dbpedia:"

    @property
    def SCHEMA_ORG_NS(self) -> str:
        """Get Schema.org namespace."""
        return self._config.namespaces.get_namespace('schemaorg') or "http://schema.org/"
    
    @property
    def SCHEMA_ORG(self) -> str:
        """Get Schema.org prefix."""
        return "schemaorg:"

    # AMR identification
    @property
    def AMR_RELATION_BEGIN(self) -> str:
        return self._config.patterns.get_constant('relationBegin') or ":"

    # Regex patterns using pattern matcher
    @property
    def AMR_VERB(self) -> str:
        return self._config.patterns.get_pattern('verb') or "-[0-9]+$"
        
    @property
    def AMR_VERB2(self) -> str:
        return self._config.patterns.get_pattern('verbFull') or ".*-[0-9]+$"
        
    @property
    def AMR_ARG(self) -> str:
        return self._config.patterns.get_pattern('argument') or ":arg."
        
    @property
    def AMR_INVERSE(self) -> str:
        return self._config.patterns.get_pattern('inverse') or ":.+[0-9]-of"
        
    @property
    def AMR_OP(self) -> str:
        return self._config.patterns.get_pattern('operator') or ":op[0-9]+"
        
    @property
    def ALL(self) -> str:
        return ".+"
        
    @property
    def AMR_SENTENCE(self) -> str:
        return self._config.patterns.get_pattern('sentence') or ":snt[0-9]$"
        
    @property
    def AMR_VAR(self) -> str:
        return self._config.patterns.get_pattern('variable') or "^[a-zA-Z][a-zA-Z]*[0-9][0-9]*$"

    # Prepositions using linguistic provider
    @property
    def AMR_PREP(self) -> str:
        return ":prep-"
        
    @property
    def AMR_PREP_AGAINST(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'against') or ":prep-against"
        
    @property
    def AMR_PREP_ALONG_WITH(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'alongWith') or ":prep-along-with"
        
    @property
    def AMR_PREP_AMID(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'amid') or ":prep-amid"
        
    @property
    def AMR_PREP_AMONG(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'among') or ":prep-among"
        
    @property
    def AMR_PREP_AS(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'as') or ":prep-as"
        
    @property
    def AMR_PREP_AT(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'at') or ":prep-at"
        
    @property
    def AMR_PREP_BY(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'by') or ":prep-by"
        
    @property
    def AMR_PREP_CONCERNING(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'concerning') or ":prep-concerning"
        
    @property
    def AMR_PREP_CONSIDERING(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'considering') or ":prep-considering"
        
    @property
    def AMR_PREP_DESPITE(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'despite') or ":prep-despite"
        
    @property
    def AMR_PREP_EXCEPT(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'except') or ":prep-except"
        
    @property
    def AMR_PREP_EXCLUDING(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'excluding') or ":prep-excluding"
        
    @property
    def AMR_PREP_FOLLOWING(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'following') or ":prep-following"
        
    @property
    def AMR_PREP_FOR(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'for') or ":prep-for"
        
    @property
    def AMR_PREP_FROM(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'from') or ":prep-from"
        
    @property
    def AMR_PREP_IN(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'in') or ":prep-in"
        
    @property
    def AMR_PREP_IN_ADDITION_TO(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'inAdditionTo') or ":prep-in-addition-to"
        
    @property
    def AMR_PREP_IN_SPITE_OF(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'inSpiteOf') or ":prep-in-spite-of"
        
    @property
    def AMR_PREP_INTO(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'into') or ":prep-into"
        
    @property
    def AMR_PREP_LIKE(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'like') or ":prep-like"
        
    @property
    def AMR_PREP_ON(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'on') or ":prep-on"
        
    @property
    def AMR_PREP_ON_BEHALF_OF(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'onBehalfOf') or ":prep-on-behalf-of"
        
    @property
    def AMR_PREP_OPPOSITE(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'opposite') or ":prep-opposite"
        
    @property
    def AMR_PREP_PER(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'per') or ":prep-per"
        
    @property
    def AMR_PREP_REGARDING(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'regarding') or ":prep-regarding"
        
    @property
    def AMR_PREP_SAVE(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'save') or ":prep-save"
        
    @property
    def AMR_PREP_SUCH_AS(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'suchAs') or ":prep-such-as"
        
    @property
    def AMR_PREP_TROUGH(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'through') or ":prep-through"
        
    @property
    def AMR_PREP_TO(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'to') or ":prep-to"
        
    @property
    def AMR_PREP_TOWARD(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'toward') or ":prep-toward"
        
    @property
    def AMR_PREP_UNDER(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'under') or ":prep-under"
        
    @property
    def AMR_PREP_UNLIKE(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'unlike') or ":prep-unlike"
        
    @property
    def AMR_PREP_VERSUS(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'versus') or ":prep-versus"
        
    @property
    def AMR_PREP_WITH(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'with') or ":prep-with"
        
    @property
    def AMR_PREP_WITHIN(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'within') or ":prep-within"
        
    @property
    def AMR_PREP_WITHOUT(self) -> str:
        return self._config.patterns.get_relation('prepositions', 'without') or ":prep-without"
        
    @property
    def AMR_CONJ_AS_IF(self) -> str:
        return ":conj-as-if"

    @property
    def AMR_ENTITY(self) -> str:
        return self._config.patterns.get_constant('entity') or "-entity"

    @property
    def AMR_MULTI_SENTENCE(self) -> str:
        return self._config.patterns.get_constant('multiSentence') or "multi-sentence"

    # Gender and linguistic terms using linguistic provider
    @property
    def CITY(self) -> str:
        return self._config.linguistics.linguistic_config.get('basicWords', {}).get('city', 'city')
        
    @property
    def FRED_MALE(self) -> str:
        return self._config.linguistics.linguistic_config.get('genderTerms', {}).get('male', 'male')
        
    @property
    def FRED_FEMALE(self) -> str:
        return self._config.linguistics.linguistic_config.get('genderTerms', {}).get('female', 'female')
        
    @property
    def FRED_NEUTER(self) -> str:
        return self._config.linguistics.linguistic_config.get('genderTerms', {}).get('neuter', 'neuter')
        
    @property
    def FRED_PERSON(self) -> str:
        return self._config.linguistics.linguistic_config.get('genderTerms', {}).get('person', 'person')
        
    @property
    def FRED_MULTIPLE(self) -> str:
        return self._config.linguistics.linguistic_config.get('genderTerms', {}).get('multiple', 'multiple')

    # FRED relation properties
    @property
    def FRED_FOR(self) -> str:
        return f"{self.FRED}for"
        
    @property
    def FRED_WITH(self) -> str:
        return f"{self.FRED}with"
        
    @property
    def FRED_LIKE(self) -> str:
        return f"{self.FRED}like"
        
    @property
    def FRED_ALTHOUGH(self) -> str:
        return f"{self.FRED}although"
        
    @property
    def FRED_IN(self) -> str:
        return f"{self.FRED}in"
        
    @property
    def FRED_AT(self) -> str:
        return f"{self.FRED}at"
        
    @property
    def FRED_OF(self) -> str:
        return f"{self.FRED}of"
        
    @property
    def FRED_ON(self) -> str:
        return f"{self.FRED}on"
        
    @property
    def FRED_ENTAILS(self) -> str:
        return f"{self.FRED}entails"
        
    @property
    def FRED_EVEN(self) -> str:
        return f"{self.FRED}Even"
        
    @property
    def FRED_WHEN(self) -> str:
        return f"{self.FRED}when"
        
    @property
    def FRED_INCLUDE(self) -> str:
        return f"{self.FRED}include"
        
    @property
    def FRED_AS_IF(self) -> str:
        return f"{self.FRED}as-if"

    # Modalities
    @property
    def AMR_DOMAIN(self) -> str:
        return self._config.patterns.get_relation('core', 'domain') or ":domain"
        
    @property
    def AMR_IMPERATIVE(self) -> str:
        return self._config.patterns.patterns_config.get('mappings', {}).get('modalityModes', {}).get('imperative', 'imperative')
        
    @property
    def AMR_EXPRESSIVE(self) -> str:
        return self._config.patterns.patterns_config.get('mappings', {}).get('modalityModes', {}).get('expressive', 'expressive')
        
    @property
    def AMR_INTERROGATIVE(self) -> str:
        return self._config.patterns.patterns_config.get('mappings', {}).get('modalityModes', {}).get('interrogative', 'interrogative')
        
    @property
    def AMR_RELATIVE_POSITION(self) -> str:
        return self._config.patterns.patterns_config.get('mappings', {}).get('modalityModes', {}).get('relativePosition', 'relative-position')

    # Pronouns using linguistic provider
    @property
    def PERSON(self) -> str:
        pronouns = self._config.linguistics.get_pronouns('person')
        return f" {' '.join(pronouns)} "
        
    @property
    def MALE(self) -> str:
        pronouns = self._config.linguistics.get_pronouns('male')
        return f" {' '.join(pronouns)} "
        
    @property
    def FEMALE(self) -> str:
        pronouns = self._config.linguistics.get_pronouns('female')
        return f" {' '.join(pronouns)} "
        
    @property
    def THING(self) -> str:
        pronouns = self._config.linguistics.get_pronouns('thing')
        return f" {' '.join(pronouns)} "
        
    @property
    def THING2(self) -> str:
        pronouns = self._config.linguistics.get_pronouns('thing2')
        return f" {' '.join(pronouns)} "
        
    @property
    def DEMONSTRATIVES(self) -> str:
        pronouns = self._config.linguistics.get_pronouns('demonstratives')
        return f" {' '.join(pronouns)} "

    @property
    def AND(self) -> str:
        return self._config.linguistics.linguistic_config.get('basicWords', {}).get('and', 'and')
        
    @property
    def OR(self) -> str:
        return "or"
        
    @property
    def IN(self) -> str:
        return self._config.linguistics.linguistic_config.get('basicWords', {}).get('in', 'in')

    @property
    def ID(self) -> str:
        return self._config.linguistics.linguistic_config.get('basicWords', {}).get('id', 'id:')

    # Dot graph generation
    @property
    def DIGRAPH_INI(self) -> str:
        return "digraph {\\n charset=\"utf-8\" \\n"
        
    @property
    def DIGRAPH_END(self) -> str:
        return "}"

    # Additional namespaces
    @property
    def AMR_NS(self) -> str:
        """Get AMR namespace."""
        return self._config.namespaces.get_namespace('amr') or "https://w3id.org/framester/amr/"
    
    @property
    def AMR(self) -> str:
        """Get AMR prefix."""
        return "amr:"

    @property
    def AMRB_NS(self) -> str:
        """Get AMRB namespace."""
        return self._config.namespaces.get_namespace('amrb') or "https://w3id.org/framester/amrb/"
    
    @property
    def AMRB(self) -> str:
        """Get AMRB prefix."""
        return "amrb:"

    @property
    def VA_NS(self) -> str:
        """Get VerbAtlas namespace."""
        return self._config.namespaces.get_namespace('va') or "http://verbatlas.org/"
    
    @property
    def VA(self) -> str:
        """Get VerbAtlas prefix."""
        return "va:"

    @property
    def BN_NS(self) -> str:
        """Get BabelNet namespace."""
        return self._config.namespaces.get_namespace('bn') or "http://babelnet.org/rdf/"
    
    @property
    def BN(self) -> str:
        """Get BabelNet prefix."""
        return "bn:"

    @property
    def WN30_SCHEMA_NS(self) -> str:
        """Get WordNet30 Schema namespace."""
        return self._config.namespaces.get_namespace('wn30schema') or "https://w3id.org/framester/wn/wn30/schema/"
    
    @property
    def WN30_SCHEMA(self) -> str:
        """Get WordNet30 Schema prefix."""
        return "wn30schema:"

    @property
    def WN30_INSTANCES_NS(self) -> str:
        """Get WordNet30 Instances namespace."""
        return self._config.namespaces.get_namespace('wn30instances') or "https://w3id.org/framester/wn/wn30/instances/"
    
    @property
    def WN30_INSTANCES(self) -> str:
        """Get WordNet30 Instances prefix."""
        return "wn30instances:"

    @property
    def FS_SCHEMA_NS(self) -> str:
        """Get Framester Schema namespace."""
        return self._config.namespaces.get_namespace('fschema') or "https://w3id.org/framester/schema/"
    
    @property
    def FS_SCHEMA(self) -> str:
        """Get Framester Schema prefix."""
        return "fschema:"

    @property
    def PB_DATA_NS(self) -> str:
        """Get PropBank Data namespace."""
        return self._config.namespaces.get_namespace('pbdata') or "https://w3id.org/framester/pb/data/"
    
    @property
    def PB_DATA(self) -> str:
        """Get PropBank Data prefix."""
        return "pbdata:"

    @property
    def PB_ROLESET_NS(self) -> str:
        """Get PropBank RoleSet namespace."""
        return self._config.namespaces.get_namespace('pbrs') or "https://w3id.org/framester/data/propbank-3.4.0/RoleSet/"
    
    @property
    def PB_ROLESET(self) -> str:
        """Get PropBank RoleSet prefix."""
        return "pbrs:"

    @property
    def PB_LOCALROLE_NS(self) -> str:
        """Get PropBank LocalRole namespace."""
        return self._config.namespaces.get_namespace('pblr') or "https://w3id.org/framester/data/propbank-3.4.0/LocalRole/"
    
    @property
    def PB_LOCALROLE(self) -> str:
        """Get PropBank LocalRole prefix."""
        return "pblr:"

    @property
    def PB_GENERICROLE_NS(self) -> str:
        """Get PropBank GenericRole namespace."""
        return self._config.namespaces.get_namespace('pbgr') or "https://w3id.org/framester/data/propbank-3.4.0/GenericRole/"
    
    @property
    def PB_GENERICROLE(self) -> str:
        """Get PropBank GenericRole prefix."""
        return "pbgr:"

    @property
    def PB_SCHEMA_NS(self) -> str:
        """Get PropBank Schema namespace."""
        return self._config.namespaces.get_namespace('pbschema') or "https://w3id.org/framester/schema/propbank/"
    
    @property
    def PB_SCHEMA(self) -> str:
        """Get PropBank Schema prefix."""
        return "pbschema:"

    @property
    def FN_FRAME_NS(self) -> str:
        """Get FrameNet Frame namespace."""
        return self._config.namespaces.get_namespace('fnframe') or "https://w3id.org/framester/framenet/abox/frame/"
    
    @property
    def FN_FRAME(self) -> str:
        """Get FrameNet Frame prefix."""
        return "fnframe:"

    @property
    def FS_SCHEMA_SUBSUMED_UNDER(self) -> str:
        return f"{self.FS_SCHEMA}subsumedUnder"

    @property
    def AMR_WIKIDATA(self) -> str:
        return self._config.patterns.get_relation('core', 'wikidata') or ":wikidata"
        
    @property
    def WIKIDATA_NS(self) -> str:
        """Get Wikidata namespace."""
        return self._config.namespaces.get_namespace('wikidata') or "http://www.wikidata.org/entity/"
    
    @property
    def WIKIDATA(self) -> str:
        """Get Wikidata prefix."""
        return "wikidata:"

    @property
    def LITERAL_NS(self) -> str:
        """Get Literal namespace."""
        return self._config.namespaces.get_namespace('literal') or ""
    
    @property
    def LITERAL(self) -> str:
        """Get Literal prefix."""
        return "literal:"
        
    @property
    def LITERAL2(self) -> str:
        return "Literal:"

    @property
    def SCHEMA_NS(self) -> str:
        """Get Schema namespace."""
        return self._config.namespaces.get_namespace('schema') or "https://schema.org/"
    
    @property
    def SCHEMA(self) -> str:
        """Get Schema prefix."""
        return "schema:"

    # Lists using configuration manager
    @property
    def PREFIX(self) -> List[str]:
        """Get all prefixes from configuration."""
        return self._config.namespaces.get_prefix_list()
        
    @property
    def NAMESPACE(self) -> List[str]:
        """Get all namespaces from configuration."""
        return self._config.namespaces.get_namespace_list()
        
    @property
    def PREFIX_NUM(self) -> int:
        """Get number of prefixes."""
        return len(self.PREFIX)

    # RDF modes using validation service
    @property
    def RDF_MODE(self) -> List[str]:
        """Get supported RDF serialization formats."""
        return self._config.validation.get_serialization_formats()
        
    @property
    def RDF_MODE_MAX(self) -> int:
        """Get number of RDF modes."""
        return len(self.RDF_MODE)

    # AMR relations and mappings from configuration
    @property
    def AMR_RELATIONS(self) -> List[str]:
        """Get list of AMR relations."""
        relations = []
        config = self._config.patterns.patterns_config
        for category in ['core', 'spatial', 'temporal', 'semantic', 'structural']:
            category_relations = config.get('relations', {}).get(category, {})
            relations.extend(category_relations.values())
        return relations

    @property
    def AMR_VARS(self) -> List[str]:
        """Get AMR variables list."""
        return [self.ALL] * len(self.AMR_RELATIONS)

    @property
    def FRED_RELATIONS(self) -> List[str]:
        """Get list of FRED relations mapped from AMR."""
        fred_mappings = self._config.patterns.patterns_config.get('mappings', {}).get('relationsToFred', {})
        return list(fred_mappings.values())

    @property
    def FRED_VARS(self) -> List[str]:
        """Get FRED variables list."""
        return [""] * len(self.FRED_RELATIONS)

    @property
    def PATTERNS_NUMBER(self) -> int:
        """Get number of patterns."""
        return len(self.AMR_RELATIONS)

    @property
    def QUOTE(self) -> str:
        return self._config.linguistics.linguistic_config.get('basicWords', {}).get('quote', '"')

    # Linguistic data methods using ConfigurationManager
    def read_adjectives(self) -> List[str]:
        """
        Read adjectives from configuration.
        
        Returns:
            List of adjectives from the linguistic data configuration.
        """
        return self._config.linguistics.get_adjectives()

    @property
    def ADJECTIVE(self) -> List[str]:
        """Get list of adjectives."""
        return self.read_adjectives()

    @property
    def MANNER_ADVERBS(self) -> List[str]:
        """Get list of manner adverbs."""
        return self._config.linguistics.get_manner_adverbs()

    @property
    def PREPOSITION(self) -> List[str]:
        """Get list of prepositions."""
        return self._config.linguistics.get_prepositions()

    @property
    def CONJUNCTION(self) -> List[str]:
        """Get list of conjunctions."""
        return self._config.linguistics.get_conjunctions()

    @property
    def QUANTITY_TYPES(self) -> List[str]:
        """Get list of quantity types."""
        return self._config.entities.get_quantity_types()

    # Special verbs
    @property
    def HAVE_ORG_ROLE(self) -> str:
        return self._config.patterns.get_special_verb('haveOrgRole') or "have-org-role-91"
        
    @property
    def HAVE_REL_ROLE(self) -> str:
        return self._config.patterns.get_special_verb('haveRelRole') or "have-rel-role-91"

    @property
    def AMR_QUANTITY(self) -> str:
        return self._config.patterns.get_pattern('quantity') or ".+-quantity$"
        
    @property
    def QUANTITY(self) -> str:
        return self._config.patterns.get_constant('quantity') or "-quantity"
        
    @property
    def SUM_OF(self) -> str:
        return self._config.patterns.get_constant('sumOf') or "sum-of"
        
    @property
    def SUM(self) -> str:
        return self._config.patterns.get_constant('sum') or "sum"
        
    @property
    def PRODUCT_OF(self) -> str:
        return self._config.patterns.get_constant('productOf') or "product-of"
        
    @property
    def PRODUCT(self) -> str:
        return self._config.patterns.get_constant('product') or "product"
        
    @property
    def EVEN_IF(self) -> str:
        return self._config.linguistics.linguistic_config.get('conditionalExpressions', {}).get('evenIf', 'even-if')
        
    @property
    def EVEN_WHEN(self) -> str:
        return self._config.linguistics.linguistic_config.get('conditionalExpressions', {}).get('evenWhen', 'even-when')

    # Date entities
    @property
    def AMR_DATE_ENTITY(self) -> str:
        return "date-entity"
        
    @property
    def AMR_DATE_CALENDAR(self) -> str:
        return ":calendar"
        
    @property
    def AMR_DATE_CENTURY(self) -> str:
        return ":century"
        
    @property
    def AMR_DATE_DAY(self) -> str:
        return ":day"
        
    @property
    def AMR_DATE_DAY_PERIOD(self) -> str:
        return ":dayperiod"
        
    @property
    def AMR_DATE_DECADE(self) -> str:
        return ":decade"
        
    @property
    def AMR_DATE_ERA(self) -> str:
        return ":era"
        
    @property
    def AMR_DATE_MONTH(self) -> str:
        return ":month"
        
    @property
    def AMR_DATE_QUARTER(self) -> str:
        return ":quarter"
        
    @property
    def AMR_DATE_SEASON(self) -> str:
        return ":season"
        
    @property
    def AMR_DATE_TIMEZONE(self) -> str:
        return ":timezone"
        
    @property
    def AMR_DATE_WEEKDAY(self) -> str:
        return ":weekday"
        
    @property
    def AMR_DATE_YEAR(self) -> str:
        return ":year"
        
    @property
    def AMR_DATE_YEAR2(self) -> str:
        return ":year2"
        
    @property
    def AMR_DATE_INTERVAL(self) -> str:
        return "date-interval"

    @property
    def PREP_SUBSTITUTION(self) -> str:
        return self._config.patterns.get_constant('prepSubstitution') or ":x->y"

    @property
    def DISJUNCT(self) -> str:
        return "disjunct"
        
    @property
    def CONJUNCT(self) -> str:
        return "conjunct"
        
    @property
    def SPECIAL_INSTANCES(self) -> List[str]:
        return [self.DISJUNCT, self.CONJUNCT]
        
    @property
    def SPECIAL_INSTANCES_PREFIX(self) -> List[str]:
        return [self.BOXING, self.BOXING]

    @property
    def AMR_VALUE_INTERVAL(self) -> str:
        return "value-interval"

    @property
    def AMR_INSTANCES(self) -> List[str]:
        """Get list of AMR instances."""
        instances = []
        config = self._config.entities.entities_config
        for category_instances in config.get('namedEntities', {}).values():
            instances.extend(category_instances)
        return instances

    @property
    def AMR_ALWAYS_INSTANCES(self) -> List[str]:
        """Get list of AMR instances that are always instances."""
        return self._config.entities.get_special_entities()

    @property
    def OP_JOINER(self) -> str:
        return self._config.patterns.get_constant('opJoiner') or "_"
        
    @property
    def OP_NAME(self) -> str:
        return self._config.patterns.get_constant('opName') or "name"

    @property
    def AMR_INTEGRATION(self) -> List[str]:
        """Get list of AMR integration relations."""
        relations = []
        config = self._config.patterns.patterns_config
        for category in ['semantic', 'spatial', 'temporal']:
            category_relations = config.get('relations', {}).get(category, {})
            relations.extend(category_relations.values())
        relations.extend([self.AMR_POLARITY, self.AMR_MOD])
        return relations

    @property
    def NON_LITERAL(self) -> str:
        return self._config.patterns.get_constant('nonLiteral') or ":"
        
    @property
    def WRONG_APOSTROPHE(self) -> str:
        return self._config.patterns.get_constant('wrongApostrophe') or "'"
        
    @property
    def RIGHT_APOSTROPHE(self) -> str:
        return self._config.patterns.get_constant('rightApostrophe') or "'"
        
    @property
    def FS_SCHEMA_SEMANTIC_ROLE(self) -> str:
        return f"{self.FS_SCHEMA}SemanticRole"

    @property
    def AGE_01(self) -> str:
        return self._config.patterns.get_special_verb('age') or "age-01"
        
    @property
    def NEW_VAR(self) -> str:
        return self._config.patterns.get_constant('newVar') or "newVar"
        
    @property
    def SCALE(self) -> str:
        return self._config.patterns.get_constant('scale') or "_scale"
        
    @property
    def PBLR_POLARITY(self) -> str:
        return "pblr:polarity"

    # Enum classes for backward compatibility
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


# Note: Static access now works through the metaclass __getattr__ method


# Create a global singleton instance for easier access
_glossary_instance = None

def get_glossary_instance() -> Glossary:
    """Get the global glossary singleton instance."""
    global _glossary_instance
    if _glossary_instance is None:
        _glossary_instance = Glossary()
    return _glossary_instance