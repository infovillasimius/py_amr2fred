import csv
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.parse
from enum import Enum
from typing import IO

import nltk
import rdflib
import requests
from SPARQLWrapper import SPARQLWrapper, POST, SPARQLWrapper2
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import OWL, NamespaceManager, Namespace
from unidecode import unidecode
from wikimapper import WikiMapper

nltk.download('wordnet')
from nltk.corpus import wordnet
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Glossary:
    ENDLESS = 1000
    ENDLESS2 = 800
    RECURSIVE_ERROR = " recursive error! "
    TOP = "top"
    INSTANCE = "instance"

    FRED = "fred:"
    FRED_NS = "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"
    DEFAULT_FRED_NS = "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"

    FRED_TOPIC = "fred:Topic"
    FRED_ABOUT = "fred:about"

    # Local name for dul:
    DUL = "dul:"

    # Local name for d0:
    D0 = "d0:"

    # Name space for dul and d0
    DUL_NS = "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"
    D0_NS = "http://www.ontologydesignpatterns.org/ont/d0.owl#"

    DUL_EVENT = DUL + "Event"
    DUL_HAS_QUALITY = DUL + "hasQuality"
    DUL_HAS_DATA_VALUE = DUL + "hasDataValue"
    DUL_ASSOCIATED_WITH = DUL + "associatedWith"
    DUL_HAS_MEMBER = DUL + "hasMember"
    DUL_HAS_PRECONDITION = DUL + "hasPrecondition"
    DUL_HAS_AMOUNT = DUL + "hasAmount"
    DUL_PRECEDES = DUL + "precedes"

    DUL_AGENT = DUL + "Agent"
    DUL_CONCEPT = DUL + "Concept"
    DUL_INFORMATION_ENTITY = DUL + "InformationEntity"
    DUL_ORGANISM = DUL + "Organism"
    DUL_ORGANIZATION = DUL + "Organization"
    DUL_PERSON = DUL + "Person"
    DUL_NATURAL_PERSON = DUL + "NaturalPerson"
    DUL_SUBSTANCE = DUL + "Substance"

    D0_LOCATION = D0 + "Location"
    D0_TOPIC = D0 + "Topic"

    DULS = [DUL_AGENT, DUL_CONCEPT, DUL_INFORMATION_ENTITY, DUL_ORGANISM, DUL_ORGANIZATION, DUL_SUBSTANCE, D0_TOPIC,
            D0_LOCATION, DUL_PERSON]
    DULS_CHECK = ["agent", "concept", "informationentity", "organism", "organization", "substance", "topic", "location",
                  "person"]

    # Local name for boxer
    BOXER = "boxer:"
    BOXER_AGENT = BOXER + "agent"
    BOXER_PATIENT = BOXER + "patient"
    BOXER_THEME = BOXER + "theme"

    # Name space for boxer
    BOXER_NS = "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#"

    # Local name for boxing
    BOXING = "boxing:"

    # Name space for boxing
    BOXING_NS = "http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#"

    BOXING_NECESSARY = "boxing:Necessary"
    BOXING_POSSIBLE = "boxing:Possible"
    BOXING_HAS_MODALITY = "boxing:hasModality"
    BOXING_FALSE = "boxing:False"
    BOXING_TRUTH = "boxing:Truth"
    BOXING_HAS_TRUTH_VALUE = "boxing:hasTruthValue"
    BOXING_UNKNOWN = "boxing:Unknown"

    # Local name for quant
    QUANT = "quant:"
    QUANT_EVERY = QUANT + "every"

    # Name space for quant
    QUANT_NS = "http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"
    QUANT_HAS_DETERMINER = "quant:hasDeterminer"
    QUANT_HAS_QUANTIFIER = "quant:hasQuantifier"

    # Local name for owl
    OWL = "owl:"

    # Name space for owl
    OWL_NS = str(rdflib.namespace.OWL)
    OWL_THING = OWL + "Thing"
    OWL_EQUIVALENT_CLASS = OWL + "equivalentClass"
    OWL_SAME_AS = OWL + "sameAs"
    OWL_OBJECT_PROPERTY = OWL + "ObjectProperty"
    OWL_INVERSE_OF = OWL + "inverseOf"
    OWL_EQUIVALENT_PROPERTY = OWL + "equivalentProperty"
    OWL_DATA_TYPE_PROPERTY = OWL + "DatatypeProperty"

    # Local name for rdf
    RDF = "rdf:"

    # Name space for rdf
    RDF_NS = str(rdflib.namespace.RDF)
    RDF_TYPE = "rdf:type"

    # Local name for rdfs
    RDFS = "rdfs:"

    # Name space for rdfs
    RDFS_NS = str(rdflib.namespace.RDFS)
    RDFS_SUBCLASS_OF = "rdfs:subClassOf"
    RDFS_SUB_PROPERTY_OF = "rdfs:subPropertyOf"
    RDFS_LABEL = "rdfs:label"

    # Local name for vn.role
    VN_ROLE = "vn.role:"
    VN_ROLE_NS = "http://www.ontologydesignpatterns.org/ont/vn/abox/role/vnrole.owl#"
    VN_ROLE_LOCATION = VN_ROLE + "Location"
    VN_ROLE_SOURCE = VN_ROLE + "Source"
    VN_ROLE_DESTINATION = VN_ROLE + "Destination"
    VN_ROLE_BENEFICIARY = VN_ROLE + "Beneficiary"
    VN_ROLE_TIME = VN_ROLE + "Time"
    VN_ROLE_INSTRUMENT = VN_ROLE + "Instrument"
    VN_ROLE_CAUSE = VN_ROLE + "Cause"
    VN_ROLE_EXPERIENCER = VN_ROLE + "Experiencer"
    VN_ROLE_THEME = VN_ROLE + "Theme"
    VN_ROLE_PREDICATE = VN_ROLE + "Predicate"

    REIFI_BENEFIT = "benefit-01"
    REIFI_HAVE_CONCESSION = "have-concession-91"
    REIFI_HAVE_CONDITION = "have-condition-91"
    REIFI_BE_DESTINED_FOR = "be-destined-for-91"
    REIFI_EXEMPLIFY = "exemplify-01"
    REIFI_HAVE_EXTENT = "have-extent-91"
    REIFI_HAVE_FREQUENCY = "have-frequency-91"
    REIFI_HAVE_INSTRUMENT = "have-instrument-91"
    REIFI_BE_LOCATED_AT = "be-located-at-91"
    REIFI_HAVE_MANNER = "have-manner-91"
    REIFI_HAVE_MOD = "have-mod-91"
    REIFI_HAVE_NAME = "have-name-91"
    REIFI_HAVE_PART = "have-part-91"
    REIFI_HAVE_POLARITY = "have-polarity-91"
    REIFI_HAVE_PURPOSE = "have-purpose-91"
    REIFI_HAVE_QUANT = "have-quant-91"
    REIFI_BE_FROM = "be-from-91"
    REIFI_HAVE_SUBEVENT = "have-subevent-91"
    REIFI_INCLUDE = "include-91"
    REIFI_BE_TEMPORALLY_AT = "be-temporally-at-91"
    REIFI_HAVE_DEGREE = "have-degree-91"
    REIFI_HAVE_LI = "have-li-91"
    RATE_ENTITY = "rate-entity-91"

    # Local name for vn.data
    VN_DATA = "vn.data:"
    VN_DATA_NS = "http://www.ontologydesignpatterns.org/ont/vn/data/"

    NN_INTEGER_NS = "http://www.w3.org/2001/XMLSchema#decimal"
    NN_INTEGER = "^[0-9]+$"
    NN_INTEGER2 = "^[0-9]+[.]*[0-9]*$"
    NN_RATIONAL = "^[1-9][0-9]*/[1-9][0-9]*$"

    DATE_SCHEMA_NS = "http://www.w3.org/2001/XMLSchema#date"
    DATE_SCHEMA = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"

    TIME_SCHEMA2_NS = "https://www.w3.org/TR/xmlschema-2/#time"
    TIME_SCHEMA2 = "time:"
    TIME_SCHEMA = "([01]?[0-9]|2[0-3]):[0-5][0-9]"

    STRING_SCHEMA_NS = "http://www.w3.org/2001/XMLSchema#string"

    DBR = "dbr:"  # "dbpedia:"
    DBR_NS = "http://dbpedia.org/resource/"

    DBO = "dbo:"
    DBO_NS = "http://dbpedia.org/ontology/"

    DBPEDIA = "dbpedia:"
    DBPEDIA_NS = "http://dbpedia.org/resource/"

    SCHEMA_ORG = "schemaorg:"
    SCHEMA_ORG_NS = "http://schema.org/"

    # for AMR elements identification
    AMR_RELATION_BEGIN = ":"

    # Regex usate dal parser
    AMR_VERB = "-[0-9]+$"
    AMR_VERB2 = ".*-[0-9]+$"
    AMR_ARG = ":arg."
    AMR_INVERSE = ":.+[0-9]-of"
    AMR_OP = ":op[0-9]+"
    ALL = ".+"
    AMR_SENTENCE = ":snt[0-9]$"
    AMR_VAR = "^[a-zA-Z][a-zA-Z]*[0-9][0-9]*$"

    # Stringhe pattern AMR tradotti
    AMR_POLARITY = ":polarity"
    AMR_POLARITY_OF = ":polarity-of"
    AMR_MINUS = "-"
    AMR_PLUS = "+"
    AMR_MODE = ":mode"
    AMR_POSS = ":poss"
    AMR_ARG0 = ":arg0"
    AMR_ARG1 = ":arg1"
    AMR_ARG2 = ":arg2"
    AMR_ARG3 = ":arg3"
    AMR_ARG4 = ":arg4"
    AMR_ARG5 = ":arg5"
    AMR_ARG6 = ":arg6"
    AMR_OP1 = ":op1"
    AMR_QUANT = ":quant"
    AMR_TOPIC = ":topic"
    AMR_UNKNOWN = "amr-unknown"
    AMR_MOD = ":mod"
    AMR_LOCATION = ":location"
    AMR_SOURCE = ":source"
    AMR_DESTINATION = ":destination"
    AMR_DIRECTION = ":direction"
    AMR_PATH = ":path"
    AMR_MANNER = ":manner"
    AMR_WIKI = ":wiki"
    AMR_NAME = ":name"
    AMR_PURPOSE = ":purpose"
    AMR_POLITE = ":polite"

    AMR_ACCOMPANIER = ":accompanier"
    AMR_AGE = ":age"
    AMR_BENEFICIARY = ":beneficiary"
    AMR_CAUSE = ":cause"
    AMR_COMPARED_TO = ":compared-to"
    AMR_CONCESSION = ":concession"
    AMR_CONDITION = ":condition"
    AMR_CONSIST_OF = ":consist-of"
    AMR_DEGREE = ":degree"
    AMR_DURATION = ":duration"
    AMR_EXAMPLE = ":example"
    AMR_EXTENT = ":extent"
    AMR_FREQUENCY = ":frequency"
    AMR_INSTRUMENT = ":instrument"
    AMR_LI = ":li"
    AMR_MEDIUM = ":medium"
    AMR_ORD = ":ord"
    AMR_PART = ":part"
    AMR_PART_OF = ":part-of"
    AMR_QUANT_OF = ":quant-of"
    AMR_RANGE = ":range"
    AMR_SCALE = ":scale"
    AMR_SUB_EVENT = ":subevent"
    AMR_SUB_EVENT_OF = ":subevent-of"
    AMR_SUBSET = ":subset"
    AMR_SUBSET_OF = ":subset-of"
    AMR_TIME = ":time"
    AMR_UNIT = ":unit"
    AMR_VALUE = ":value"

    AMR_PREP = ":prep-"
    AMR_PREP_AGAINST = ":prep-against"
    AMR_PREP_ALONG_WITH = ":prep-along-with"
    AMR_PREP_AMID = ":prep-amid"
    AMR_PREP_AMONG = ":prep-among"
    AMR_PREP_AS = ":prep-as"
    AMR_PREP_AT = ":prep-at"
    AMR_PREP_BY = ":prep-by"
    AMR_PREP_CONCERNING = ":prep-concerning"
    AMR_PREP_CONSIDERING = ":prep-considering"
    AMR_PREP_DESPITE = ":prep-despite"
    AMR_PREP_EXCEPT = ":prep-except"
    AMR_PREP_EXCLUDING = ":prep-excluding"
    AMR_PREP_FOLLOWING = ":prep-following"
    AMR_PREP_FOR = ":prep-for"
    AMR_PREP_FROM = ":prep-from"
    AMR_PREP_IN = ":prep-in"
    AMR_PREP_IN_ADDITION_TO = ":prep-in-addition-to"
    AMR_PREP_IN_SPITE_OF = ":prep-in-spite-of"
    AMR_PREP_INTO = ":prep-into"
    AMR_PREP_LIKE = ":prep-like"
    AMR_PREP_ON = ":prep-on"
    AMR_PREP_ON_BEHALF_OF = ":prep-on-behalf-of"
    AMR_PREP_OPPOSITE = ":prep-opposite"
    AMR_PREP_PER = ":prep-per"
    AMR_PREP_REGARDING = ":prep-regarding"
    AMR_PREP_SAVE = ":prep-save"
    AMR_PREP_SUCH_AS = ":prep-such-as"
    AMR_PREP_TROUGH = ":prep-through"
    AMR_PREP_TO = ":prep-to"
    AMR_PREP_TOWARD = ":prep-toward"
    AMR_PREP_UNDER = ":prep-under"
    AMR_PREP_UNLIKE = ":prep-unlike"
    AMR_PREP_VERSUS = ":prep-versus"
    AMR_PREP_WITH = ":prep-with"
    AMR_PREP_WITHIN = ":prep-within"
    AMR_PREP_WITHOUT = ":prep-without"
    AMR_CONJ_AS_IF = ":conj-as-if"

    AMR_ENTITY = "-entity"

    AMR_MULTI_SENTENCE = "multi-sentence"

    # Stringhe utilizzate durante la traduzione
    OF = "Of"
    BY = "By"
    CITY = "city"
    FRED_MALE = "male"
    FRED_FEMALE = "female"
    FRED_NEUTER = "neuter"
    FRED_PERSON = "person"
    FRED_MULTIPLE = "multiple"
    FRED_FOR = FRED + "for"
    FRED_WITH = FRED + "with"
    FRED_LIKE = FRED + "like"
    FRED_ALTHOUGH = FRED + "although"
    FRED_IN = FRED + "in"
    FRED_AT = FRED + "at"
    FRED_OF = FRED + "of"
    FRED_ON = FRED + "on"
    FRED_ENTAILS = FRED + "entails"
    FRED_EVEN = FRED + "Even"
    FRED_WHEN = FRED + "when"
    FRED_INCLUDE = FRED + "include"
    FRED_AS_IF = FRED + "as-if"

    AMR_DOMAIN = ":domain"
    AMR_IMPERATIVE = "imperative"
    AMR_EXPRESSIVE = "expressive"
    AMR_INTERROGATIVE = "interrogative"
    AMR_RELATIVE_POSITION = "relative-position"

    # Stringhe usate per il riconoscimento dal parser
    PERSON = " I i you You YOU we We WE they They THEY "
    MALE = " he He HE "
    FEMALE = " she She SHE "
    THING = " It it IT that those this these "
    THING2 = " It it IT "
    DEMONSTRATIVES = " that those this these "
    AND = "and"
    OR = "or"
    IN = "in"

    ID = "id:"

    # Stringhe usate per la generazione del grafico .dot
    DIGRAPH_INI = "digraph {\n charset=\"utf-8\" \n"
    DIGRAPH_END = "}"

    # Nuovi prefissi e nuovi Spazi Nomi
    AMR_NS = "https://w3id.org/framester/amr/"
    AMR = "amr:"

    AMRB_NS = "https://w3id.org/framester/amrb/"
    AMRB = "amrb:"

    VA_NS = "http://verbatlas.org/"
    VA = "va:"

    BN_NS = "http://babelnet.org/rdf/"
    BN = "bn:"

    WN30_SCHEMA_NS = "https://w3id.org/framester/wn/wn30/schema/"
    WN30_SCHEMA = "wn30schema:"

    WN30_INSTANCES_NS = "https://w3id.org/framester/wn/wn30/instances/"
    WN30_INSTANCES = "wn30instances:"

    FS_SCHEMA_NS = "https://w3id.org/framester/schema/"
    FS_SCHEMA = "fschema:"

    PB_DATA_NS = "https://w3id.org/framester/pb/data/"
    PB_DATA = "pbdata:"

    PB_ROLESET_NS = "https://w3id.org/framester/data/propbank-3.4.0/RoleSet/"
    PB_ROLESET = "pbrs:"

    PB_LOCALROLE_NS = "https://w3id.org/framester/data/propbank-3.4.0/LocalRole/"
    PB_LOCALROLE = "pblr:"

    PB_GENERICROLE_NS = "https://w3id.org/framester/data/propbank-3.4.0/GenericRole/"
    PB_GENERICROLE = "pbgr:"

    PB_SCHEMA_NS = "https://w3id.org/framester/schema/propbank/"
    PB_SCHEMA = "pbschema:"

    FN_FRAME_NS = "https://w3id.org/framester/framenet/abox/frame/"
    FN_FRAME = "fnframe:"

    FS_SCHEMA_SUBSUMED_UNDER = FS_SCHEMA + "subsumedUnder"

    AMR_WIKIDATA = ":wikidata"
    WIKIDATA = "wikidata:"
    WIKIDATA_NS = "http://www.wikidata.org/entity/"

    LITERAL = "literal:"
    LITERAL2 = "Literal:"
    LITERAL_NS = ""

    SCHEMA = "schema:"
    SCHEMA_NS = "https://schema.org/"

    # Array of Fred elements local names
    PREFIX = [FRED, DUL, BOXER, BOXING, QUANT, VN_ROLE, RDF, RDFS, OWL, VN_DATA, DBPEDIA, SCHEMA_ORG, AMR, VA, BN,
              WN30_SCHEMA, WN30_INSTANCES, FS_SCHEMA, PB_DATA, PB_ROLESET, PB_LOCALROLE, PB_GENERICROLE,
              PB_SCHEMA, FN_FRAME, PB_LOCALROLE, WIKIDATA, D0, TIME_SCHEMA2, AMRB, LITERAL, SCHEMA]

    # Array of fred elements name space
    NAMESPACE = [FRED_NS, DUL_NS, BOXER_NS, BOXING_NS, QUANT_NS, VN_ROLE_NS, RDF_NS, RDFS_NS, OWL_NS, VN_DATA_NS,
                 DBPEDIA_NS, SCHEMA_ORG_NS, AMR_NS, VA_NS, BN_NS, WN30_SCHEMA_NS, WN30_INSTANCES_NS, FS_SCHEMA_NS,
                 PB_DATA_NS, PB_ROLESET_NS, PB_LOCALROLE_NS, PB_GENERICROLE_NS, PB_SCHEMA_NS, FN_FRAME_NS,
                 PB_LOCALROLE_NS, WIKIDATA_NS, D0_NS, TIME_SCHEMA2_NS, AMRB_NS, LITERAL_NS, SCHEMA_NS]

    # Fred's element names number
    PREFIX_NUM = len(PREFIX)

    # rdflib's writers output modes
    RDF_MODE = ["json-ld", "n3", "nquads", "nt", "hext", "pretty-xml", "trig", "trix", "turtle", "longturtle", "xml"]

    class RdflibMode(Enum):
        JSON_LD = "json-ld"
        N3 = "n3"
        NT = "nt"
        XML = "xml"
        TURTLE = "turtle"

    # Number of Jena's writers output modes
    RDF_MODE_MAX = len(RDF_MODE)

    AMR_RELATIONS = [AMR_MOD, AMR_POLARITY, AMR_TOPIC,
                     AMR_LOCATION, AMR_SOURCE, AMR_DESTINATION, AMR_DIRECTION,
                     AMR_PATH, AMR_MANNER, AMR_PURPOSE, AMR_ACCOMPANIER, AMR_BENEFICIARY,
                     AMR_TIME, AMR_INSTRUMENT, AMR_DEGREE, AMR_DURATION, AMR_CAUSE, AMR_EXAMPLE,
                     AMR_MEDIUM, AMR_CONCESSION, AMR_SUB_EVENT_OF, AMR_EXTENT, AMR_RANGE,
                     AMR_SUBSET, AMR_SUBSET_OF, AMR_FREQUENCY, AMR_PART]

    AMR_VARS = [ALL, AMR_MINUS, ALL, ALL, ALL, ALL, ALL,
                ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL, ALL]

    FRED_RELATIONS = [DUL_HAS_QUALITY, BOXING_HAS_TRUTH_VALUE,
                      FRED_ABOUT, VN_ROLE_LOCATION, VN_ROLE_SOURCE, VN_ROLE_DESTINATION, VN_ROLE_DESTINATION,
                      VN_ROLE_LOCATION, DUL_HAS_QUALITY, VN_ROLE_PREDICATE, FRED_WITH, VN_ROLE_BENEFICIARY,
                      VN_ROLE_TIME, VN_ROLE_INSTRUMENT, DUL_HAS_QUALITY, AMR + AMR_DURATION[1:], VN_ROLE_CAUSE,
                      FRED_LIKE, AMR + AMR_MEDIUM[1:], FRED_ALTHOUGH, FRED_IN, DUL_HAS_QUALITY, FRED_IN, FRED_INCLUDE,
                      FRED_OF, DUL_ASSOCIATED_WITH, FRED_WITH]

    FRED_VARS = ["", BOXING_FALSE, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                 "", "", "", ""]

    PATTERNS_NUMBER = len(AMR_RELATIONS)

    QUOTE = "\""

    @staticmethod
    def read_adjectives():
        current_directory = os.path.dirname(__file__)
        try:
            with open(os.path.join(current_directory, "adjectives.json"), "r", encoding="utf-8") as adjectives_file:
                adj = json.load(adjectives_file)
                return adj
        except Exception as e:
            logger.warning(e)
            return []

    ADJECTIVE = read_adjectives()

    MANNER_ADVERBS = ["accidentally", "angrily", "anxiously",
                      "awkwardly", "badly", "beautifully", "blindly", "boldly", "bravely", "brightly",
                      "busily", "calmly", "carefully", "carelessly", "cautiously", "cheerfully",
                      "clearly", "closely", "correctly", "courageously", "cruelly", "daringly",
                      "deliberately", "doubtfully", "eagerly", "easily", "elegantly", "enormously",
                      "enthusiastically", "equally", "eventually", "exactly", "faithfully", "fast",
                      "fatally", "fiercely", "fondly", "foolishly", "fortunately", "frankly",
                      "frantically", "generously", "gently", "gladly", "gracefully", "greedily",
                      "happily", "hard", "hastily", "healthily", "honestly", "hungrily", "hurriedly",
                      "inadequately", "ingeniously", "innocently", "inquisitively", "irritably",
                      "joyously", "justly", "kindly", "lazily", "loosely", "loudly", "madly",
                      "mortally", "mysteriously", "neatly", "nervously", "noisily", "obediently",
                      "openly", "painfully", "patiently", "perfectly", "politely", "poorly",
                      "powerfully", "promptly", "punctually", "quickly", "quietly", "rapidly",
                      "rarely", "really", "recklessly", "regularly", "reluctantly", "repeatedly",
                      "rightfully", "roughly", "rudely", "sadly", "safely", "selfishly", "sensibly",
                      "seriously", "sharply", "shyly", "silently", "sleepily", "slowly", "smoothly",
                      "so", "softly", "solemnly", "speedily", "stealthily", "sternly", "straight",
                      "stupidly", "successfully", "suddenly", "suspiciously", "swiftly", "tenderly",
                      "tensely", "thoughtfully", "tightly", "truthfully", "unexpectedly", "victoriously",
                      "violently", "vivaciously", "warmly", "weakly", "wearily", "well", "wildly",
                      "wisely"]

    PREPOSITION = ["à-la", "aboard", "about", "above", "according-to", "across", "after", "against", "ahead-of",
                   "along", "along-with", "alongside", "amid", "amidst-", "among-", "amongst", "anti", "apart-from",
                   "around-", "as", "as-for", "as-per", "as-to", "as-well-as", "aside-from",
                   "astride", "at", "atop", "away-from", "bar", "barring", "because-of",
                   "before", "behind", "below", "beneath", "beside", "besides", "between",
                   "beyond", "but", "but-for", "by", "by-means-of", "circa", "close-to",
                   "concerning", "considering", "contrary-to", "counting", "cum", "depending-on",
                   "despite", "down", "due-to", "during", "except", "except-for", "excepting",
                   "excluding", "following", "for", "forward-of", "from", "further-to", "given",
                   "gone", "in", "in-addition-to", "in-between", "in-case-of", "in-the-face-of",
                   "in-favor-of", "in-front-of", "in-lieu-of", "in-spite-of", "in-view-of",
                   "including", "inside", "instead-of", "into", "irrespective-of", "less",
                   "like", "minus", "near", "near-to", "next-to", "notwithstanding", "of",
                   "off", "on", "on-account-of", "on-behalf-of", "on-board", "on-to", "on-top-of",
                   "onto", "opposite", "opposite-to", "other-than", "out-of", "outside",
                   "outside-of", "over", "owing-to", "past", "pending", "per", "preparatory-to",
                   "prior-to", "plus", "pro", "re", "regarding", "regardless-of", "respecting",
                   "round", "save", "save-for", "saving", "since", "than", "thanks-to", "through",
                   "throughout", "till", "to", "together-with", "touching", "toward", "towards",
                   "under", "underneath", "unlike", "until", "up", "up-against", "up-to",
                   "up-until", "upon", "versus", "via", "vis-a-vis", "with", "with-reference-to",
                   "with-regard-to", "within", "without", "worth", "exact"]

    CONJUNCTION = ["and", "or", "but", "nor", "so", "for",
                   "yet", "after", "although", "as-", "as-if", "as-long", "as-because", "before-",
                   "even-if-", "even-though", "once", "since", "so-that", "though", "till",
                   "unless", "until", "what", "when", "whenever", "wherever", "whether", "while"]

    QUANTITY_TYPES = ["monetary-quantity", "distance-quantity",
                      "area-quantity", "volume-quantity", "temporal-quantity", "frequency-quantity",
                      "speed-quantity", "acceleration-quantity", "mass-quantity", "force-quantity",
                      "pressure-quantity", "energy-quantity", "power-quantity", "voltage-quantity",
                      "charge-quantity", "potential-quantity", "resistance-quantity", "inductance-quantity",
                      "magnetic-field-quantity", "magnetic-flux-quantity", "radiation-quantity",
                      "concentration-quantity", "temperature-quantity", "score-quantity",
                      "fuel-consumption-quantity", "seismic-quantity"]

    # Special verb for roles in organizations
    HAVE_ORG_ROLE = "have-org-role-91"

    # Special verb for relations between persons
    HAVE_REL_ROLE = "have-rel-role-91"

    AMR_QUANTITY = ".+-quantity$"
    QUANTITY = "-quantity"
    SUM_OF = "sum-of"
    SUM = "sum"
    PRODUCT_OF = "product-of"
    PRODUCT = "product"
    EVEN_IF = "even-if"
    EVEN_WHEN = "even-when"

    AMR_DATE_ENTITY = "date-entity"
    AMR_DATE_CALENDAR = ":calendar"
    AMR_DATE_CENTURY = ":century"
    AMR_DATE_DAY = ":day"
    AMR_DATE_DAY_PERIOD = ":dayperiod"
    AMR_DATE_DECADE = ":decade"
    AMR_DATE_ERA = ":era"
    AMR_DATE_MONTH = ":month"
    AMR_DATE_QUARTER = ":quarter"
    AMR_DATE_SEASON = ":season"
    AMR_DATE_TIMEZONE = ":timezone"
    AMR_DATE_WEEKDAY = ":weekday"
    AMR_DATE_YEAR = ":year"
    AMR_DATE_YEAR2 = ":year2"
    AMR_DATE_INTERVAL = "date-interval"

    PREP_SUBSTITUTION = ":x->y"

    # Node types in AMR
    class NodeType(Enum):
        NOUN = 0
        VERB = 1
        OTHER = 2
        AMR2FRED = 3
        FRED = 4
        COMMON = 5

    # Node status(used in parser)
    class NodeStatus(Enum):
        OK = 0
        AMR = 1
        ERROR = 2
        REMOVE = 3

    # Field names of propbankframe table
    class PropbankFrameFields(Enum):
        PB_Frame = 0
        PB_FrameLabel = 1
        PB_Role = 2
        FN_Frame = 3
        VA_Frame = 4

    # Field names of propbankrole table
    class PropbankRoleFields(Enum):
        PB_Frame = 0
        PB_Role = 1
        PB_RoleLabel = 2
        PB_GenericRole = 3
        PB_Tr = 4
        PB_ARG = 5
        VA_Role = 6

    DISJUNCT = "disjunct"
    CONJUNCT = "conjunct"
    SPECIAL_INSTANCES = [DISJUNCT, CONJUNCT]
    SPECIAL_INSTANCES_PREFIX = [BOXING, BOXING]

    AMR_VALUE_INTERVAL = "value-interval"

    AMR_INSTANCES = ["thing", "person", "family", "animal", "language", "nationality", "ethnic-group", "regional-group",
                     "religious-group", "political-movement", "organization", "company", "government-organization",
                     "military", "criminal-organization", "political-party", "market-sector", "school", "university",
                     "research-institute", "team", "league", "location", "city", "city-district", "county", "state",
                     "province", "territory", "country", "local-region", "country-region", "world-region", "continent",
                     "ocean", "sea", "lake", "river", "gulf", "bay", "strait", "canal", "peninsula", "mountain",
                     "volcano", "valley", "canyon", "island", "desert", "forest", "moon", "planet", "star",
                     "constellation", "facility", "airport", "station", "port", "tunnel", "bridge", "road",
                     "railway-line", "canal", "building", "theater", "museum", "palace", "hotel", "worship-place",
                     "market", "sports-facility", "park", "zoo", "amusement-park", "event", "incident",
                     "natural-disaster", "earthquake", "war", "conference", "game", "festival", "product", "vehicle",
                     "ship", "aircraft", "aircraft-type", "spaceship", "car-make", "work-of-art", "picture", "music",
                     "show", "broadcast-program", "publication", "book", "newspaper", "magazine", "journal",
                     "natural-object", "award", "law", "court-decision", "treaty", "music-key", "musical-note",
                     "food-dish", "writing-script", "variable", "program", "molecular-physical-entity",
                     "small-molecule", "protein", "protein-family", "protein-segment", "amino-acid",
                     "macro-molecular-complex", "enzyme", "nucleic-acid", "pathway", "gene", "dna-sequence", "cell",
                     "cell-line", "species", "taxon", "disease", "medical-condition"]

    AMR_ALWAYS_INSTANCES = [AMR_DATE_ENTITY, AMR_DATE_INTERVAL, "percentage-entity", "phone-number-entity",
                            "email-address-entity", "url-entity", "score-entity", "string-entity", AMR_VALUE_INTERVAL]

    OP_JOINER = "_"
    OP_NAME = "name"

    AMR_INTEGRATION = [AMR_ACCOMPANIER, AMR_BENEFICIARY, AMR_CAUSE, AMR_CONCESSION, AMR_DEGREE, AMR_DESTINATION,
                       AMR_DIRECTION, AMR_DURATION, AMR_EXAMPLE, AMR_EXTENT, AMR_FREQUENCY, AMR_INSTRUMENT,
                       AMR_LOCATION,
                       AMR_MANNER, AMR_MEDIUM, AMR_MOD, AMR_PART, AMR_PATH, AMR_POLARITY, AMR_PURPOSE, AMR_RANGE,
                       AMR_SOURCE, AMR_SUB_EVENT_OF, AMR_SUBSET, AMR_SUBSET_OF, AMR_TIME, AMR_TOPIC, AMR_AGE]

    NON_LITERAL = ":"
    WRONG_APOSTROPHE = "’"
    RIGHT_APOSTROPHE = "'"
    FS_SCHEMA_SEMANTIC_ROLE = FS_SCHEMA + "SemanticRole"

    AGE_01 = "age-01"
    NEW_VAR = "newVar"
    SCALE = "_scale"
    PBLR_POLARITY = "pblr:polarity"


class Couple:
    def __init__(self, occurrence, word):
        self.__occurrence = occurrence
        self.__word = word

    def __str__(self):
        return "\nWord: " + self.__word + " - occurrences: " + str(self.__occurrence)

    def get_word(self):
        return self.__word

    def get_occurrence(self):
        return self.__occurrence

    def set_occurrence(self, occurrence):
        self.__occurrence = occurrence

    def increment_occurrence(self):
        self.__occurrence += 1


class Node:
    unique_id = 0
    level = 0

    def __init__(self, var, relation, status=Glossary.NodeStatus.AMR, visibility=True):
        self.relation: str = relation
        self.label: str = ""
        self.var: str = var
        self.node_list: list[Node] = []
        self.parent: Node | None = None
        self.parent_list: list[Node] = []
        self.visibility: bool = visibility
        self.prefix: bool = False
        self.status: Glossary.NodeStatus = status
        self.node_type: Glossary.NodeType = Glossary.NodeType.OTHER
        self.__node_id: int = Node.unique_id
        Node.unique_id += 1
        self.verb: str = var
        self.malformed: bool = False

    def __str__(self):
        if Parser.endless > Glossary.ENDLESS:
            return Glossary.RECURSIVE_ERROR
        stringa = "\n" + "\t" * Node.level
        if self.relation != Glossary.TOP:
            stringa = stringa + "{" + self.relation + " -> " + self.var + " -> "
        else:
            stringa = "{" + self.var + " -> "

        if len(self.node_list) > 0:
            Node.level += 1
            stringa = stringa + "[" + ", ".join([str(n) for n in self.node_list]) + ']}'
            Node.level -= 1
        else:
            stringa = stringa + "[" + ", ".join([str(n) for n in self.node_list]) + ']}'

        if self.status != Glossary.NodeStatus.OK and self.relation != Glossary.TOP:
            stringa = "\n" + "\t" * Node.level + "<error" + str(Node.level) + ">" + stringa + "</error" + str(
                Node.level) + ">"
        return stringa

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.__node_id == other.__node_id

    def to_string(self) -> str:
        if not self.visibility:
            return ""
        if Parser.endless > Glossary.ENDLESS:
            return Glossary.RECURSIVE_ERROR
        stringa = "\n" + "\t" * Node.level
        if self.relation != Glossary.TOP:
            stringa = stringa + "{" + self.relation + " -> " + self.var + " -> "
        else:
            stringa = "{" + self.var + " -> "

        if len(self.node_list) > 0:
            Node.level += 1
            stringa = stringa + "[" + ", ".join([n.to_string() for n in self.node_list]) + ']}'
            Node.level -= 1
        else:
            stringa = stringa + "[" + ", ".join([n.to_string() for n in self.node_list]) + ']}'

        return stringa

    def get_instance(self):
        """
        :rtype: Node
        """
        for node in self.node_list:
            if node.relation == Glossary.INSTANCE:
                return node
        return None

    def get_child(self, relation: str):
        """
        :rtype: Node
        """
        if isinstance(relation, str):
            for node in self.node_list:
                if node.relation == relation:
                    return node
        return None

    def get_inverse(self):
        """
        :rtype: Node
        """
        for node in self.node_list:
            if (re.search(Glossary.AMR_INVERSE, node.relation) and
                    node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                    node.relation != Glossary.AMR_CONSIST_OF and
                    node.relation != Glossary.AMR_PART_OF and
                    node.relation != Glossary.AMR_SUB_EVENT_OF and
                    node.relation != Glossary.AMR_QUANT_OF and
                    node.relation != Glossary.AMR_SUBSET_OF):
                return node
        return None

    def get_inverses(self, nodes=None):
        """
        :rtype: list[Node]
        """
        if nodes is None:
            nodes: list[Node] = []
            for node in self.node_list:
                if (re.match(Glossary.AMR_INVERSE, node.relation) and
                        node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                        node.relation != Glossary.AMR_CONSIST_OF and
                        node.relation != Glossary.AMR_PART_OF and
                        node.relation != Glossary.AMR_SUB_EVENT_OF and
                        node.relation != Glossary.AMR_QUANT_OF and
                        node.relation != Glossary.AMR_SUBSET_OF and
                        node.status != Glossary.NodeStatus.REMOVE):
                    nodes.append(node)
        else:
            for node in self.node_list:
                if (re.match(Glossary.AMR_INVERSE, node.relation) and
                        node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                        node.relation != Glossary.AMR_CONSIST_OF and
                        node.relation != Glossary.AMR_PART_OF and
                        node.relation != Glossary.AMR_SUB_EVENT_OF and
                        node.relation != Glossary.AMR_QUANT_OF and
                        node.relation != Glossary.AMR_SUBSET_OF and
                        node.status != Glossary.NodeStatus.REMOVE):
                    nodes.append(node)
                nodes = node.get_inverses(nodes)
        return nodes

    def make_equals(self, node=None, node_id=None):
        if node is not None:
            self.__node_id = node.__node_id
        elif node_id is not None:
            self.__node_id = node_id

    def add(self, node):
        self.node_list.append(node)
        node.parent = self

    def get_copy(self, node=None, relation=None, parser_nodes_copy=None):
        """
        :rtype: Node
        """
        if Parser.endless > Glossary.ENDLESS:
            return None

        if node is None and relation is None and parser_nodes_copy is None:
            Parser.endless += 1
            new_node = Node(self.var, self.relation, self.status)
            new_node.__node_id = self.__node_id
            for n in self.node_list:
                new_node.add(n.get_copy())
            return new_node

        if node is None and relation is not None and parser_nodes_copy is None:
            new_node = Node(self.var, relation, self.status)
            new_node.__node_id = self.__node_id
            return new_node

        if node is not None and relation is not None and parser_nodes_copy is None:
            new_node = Node(node.var, relation, node.status)
            new_node.__node_id = node.__node_id
            for n in node.node_list:
                new_node.add(n)
            return new_node

        if node is None and relation is None and parser_nodes_copy is not None:
            Parser.endless += 1
            new_node = Node(self.var, self.relation, self.status)
            new_node.__node_id = self.__node_id
            parser_nodes_copy.append(new_node)
            for n in self.node_list:
                new_node.add(n)
            return new_node

    def get_snt(self):
        """
        :rtype: list[Node]
        """
        snt: list[Node] = []
        for node in self.node_list:
            if re.match(Glossary.AMR_SENTENCE, node.relation):
                snt.append(node)

        for node in self.node_list:
            snt += node.get_snt()
        return snt

    def get_args(self):
        """
        :rtype: list[Node]
        """
        args_list: list[Node] = []
        for node in self.node_list:
            if re.match(Glossary.AMR_ARG, node.relation.lower()):
                args_list.append(node)
        return args_list

    def get_node_id(self) -> int:
        return self.__node_id

    def get_nodes_with_parent_list_not_empty(self) -> list:
        snt = []
        for node in self.node_list:
            if len(node.parent_list) != 0:
                snt.append(node)
        return snt

    def get_children(self, relation):
        """
        :rtype: list[Node]
        """
        node_list: list[Node] = []
        for node in self.node_list:
            if node.relation == relation:
                node_list.append(node)
        return node_list

    def add_all(self, node_list):
        if isinstance(node_list, list):
            for node in node_list:
                node.parent = self
            self.node_list += node_list

    def set_status(self, status: Glossary.NodeStatus):
        self.status = status

    def get_ops(self):
        """
        :rtype: list[Node]
        """
        ops_list: list[Node] = []
        for node in self.node_list:
            if re.match(Glossary.AMR_OP, node.relation):
                ops_list.append(node)
        return ops_list

    def get_poss(self):
        """
        :rtype: Node
        """
        for node in self.node_list:
            if re.match(Glossary.AMR_POSS, node.relation):
                return node

    def substitute(self, node):
        if isinstance(node, Node):
            self.var = node.var
            self.relation = node.relation
            self.__node_id = node.__node_id
            self.node_list = []
            self.add_all(node.node_list)
            self.status = node.status
            self.node_type = node.node_type
            self.verb = node.verb

    def get_tree_status(self):
        if Parser.endless > Glossary.ENDLESS:
            return 1000000

        somma = self.status.value  # Assuming `status` is an Enum and `ordinal()` is similar to `value` in Python Enum
        for n in self.node_list:
            somma += n.get_tree_status()

        return somma


class Propbank:
    current_directory = os.path.dirname(__file__)
    SEPARATOR = "\t"
    FILE1 = os.path.join(current_directory, "propbankrolematrixaligned340.tsv")
    FILE2 = os.path.join(current_directory, "propbankframematrix340.tsv")
    __propbank = None

    def __init__(self):
        self.role_matrix = self.file_read(Propbank.FILE1)
        self.frame_matrix = self.file_read(Propbank.FILE2)

    @staticmethod
    def get_propbank():
        """
        :rtype: Propbank
        """
        if Propbank.__propbank is None:
            Propbank.__propbank = Propbank()
        return Propbank.__propbank

    @staticmethod
    def file_read(file_name, delimiter="\t", encoding="utf8"):
        file = open(file_name, encoding=encoding)
        rate = csv.reader(file, delimiter=delimiter)
        header = []
        rows = []
        for i, row in enumerate(rate):
            if i == 0:
                header = row
            if i > 0:
                rows.append(row)
        return [header, rows]

    def frame_find(self, word, frame_field: Glossary.PropbankFrameFields) -> list:
        frame_list = []
        for frame in self.frame_matrix[1]:
            if word.casefold() == frame[frame_field.value].casefold():
                frame_list.append(frame)
        return frame_list

    def role_find(self, word, role_field, value, role_field_2) -> list:
        role_list = []
        for role in self.role_matrix[1]:
            if (word.casefold() == role[role_field.value].casefold()
                    and value.casefold() == role[role_field_2.value].casefold()):
                role_list.append(role)
        return role_list

    def list_find(self, word, args: list[Node]) -> list[Node] | None:
        result = []
        num = len(args)
        cfr = 0
        if Glossary.PB_ROLESET not in word:
            word = Glossary.PB_ROLESET + word
        for node in args:
            r = Glossary.PB_SCHEMA + node.relation[1:]
            res = self.role_find(r, Glossary.PropbankRoleFields.PB_ARG, word, Glossary.PropbankRoleFields.PB_Frame)
            if len(res) > 0:
                result.append(res[0])
                cfr += 1
        if cfr >= num:
            return result
        return None


class Parser:
    __parser = None
    endless = 0
    endless2 = 0

    def __init__(self):
        self.nodes = []
        self.nodes_copy = []
        self.couples = []
        self.removed = []
        self.to_add = []
        self.vars = []
        self.root_copy = None
        self.topic_flag = True
        Parser.__parser = self

    @staticmethod
    def get_parser():
        """
        :rtype: Parser
        """
        if Parser.__parser is None:
            Parser.__parser = Parser()
        return Parser.__parser

    def reinitialise(self):
        self.nodes = []
        self.nodes_copy = []
        self.couples = []
        self.removed = []
        self.to_add = []
        self.vars = []
        self.root_copy = None
        self.topic_flag = True

    def string2array(self, amr: str) -> list[str] | None:
        word_list = []
        amr = self.normalize(amr)

        try:
            while len(amr) > 1:
                inizio = amr.index(" ") + 1
                fine = amr.index(" ", inizio)
                word = amr[inizio:fine]

                if not word.startswith(Glossary.QUOTE):
                    word_list.append(word.lower())
                else:
                    fine = amr.index(Glossary.QUOTE, inizio + 1)
                    word = amr[inizio: fine]
                    word = word.strip()
                    while "  " in word:
                        word = word.replace("  ", " ")

                    word = word.replace(" ", "_")
                    word = word.replace("__", "_")
                    word = word.replace("(_", "(")
                    word = word.replace("_)", ")")
                    word = word.replace("_/_", "/")
                    while Glossary.QUOTE in word:
                        word = word.replace(Glossary.QUOTE, "")

                    word_list.append(Glossary.LITERAL + word.replace(Glossary.QUOTE, ""))

                amr = amr[fine:]

        except Exception as e:
            logger.warning(e)
            return None

        return word_list

    @staticmethod
    def normalize(amr: str) -> str:
        re.sub("\r\n|\r|\n", " ", amr)
        amr = amr.replace("\r", " ").replace("\n", " ")
        amr = amr.strip()
        amr = amr.replace("(", " ( ")
        amr = amr.replace(")", " ) ")
        amr = amr.replace("/", " / ")
        amr = amr.replace("\t", " ")
        while "  " in amr:
            amr = amr.replace("  ", " ")
        return amr

    @staticmethod
    def strip_accents(amr: str) -> str:
        return unidecode(amr)

    def get_nodes(self, relation, amr_list) -> Node | None:
        if amr_list is None or len(amr_list) == 0:
            return None
        root = Node(var=amr_list[1], relation=relation)
        self.nodes.append(root)
        liv = 0
        i = 0
        while i < len(amr_list):
            word = amr_list[i]
            match word:
                case "(":
                    liv += 1
                    if liv == 2:
                        liv2 = 0
                        new_list = []
                        j = i
                        while j < len(amr_list):
                            word2 = amr_list[j]
                            match word2:
                                case "(":
                                    liv2 += 1
                                    new_list.append(word2)
                                case ")":
                                    liv2 -= 1
                                    new_list.append(word2)
                                    if liv2 == 0:
                                        root.add(self.get_nodes(amr_list[i - 1], new_list))
                                        i = j
                                        j = len(amr_list)
                                        liv -= 1
                                case _:
                                    new_list.append(word2)
                            j += 1
                case ")":
                    liv -= 1
                case "/":
                    for node in self.nodes:
                        if node.var == root.var and node.get_instance() is None:
                            node.make_equals(node=root)
                    root.add(Node(amr_list[i + 1], Glossary.INSTANCE))
                case _:
                    pass
                    try:
                        pass
                        if word[0] == ":" and len(amr_list) > i + 1 and amr_list[i + 1] != "(":
                            flag = False
                            for node in self.nodes:
                                if node.var == amr_list[i + 1]:
                                    new_node = node.get_copy(relation=word)
                                    root.add(new_node)
                                    self.nodes.append(new_node)
                                    flag = True
                                    break

                            if not flag:
                                new_node = Node(amr_list[i + 1], word)
                                root.add(new_node)
                                self.nodes.append(new_node)

                    except Exception as e:
                        logger.warning(e)
                        new_node = Node(amr_list[i + 1], word)
                        root.add(new_node)
                        self.nodes.append(new_node)
            i += 1
        if liv != 0:
            return None
        return root

    def check(self, root: Node) -> Node | None:
        if not isinstance(root, Node):
            return root
        if root.status != Glossary.NodeStatus.OK:
            return None
        for i, node in enumerate(root.node_list):
            if node.status != Glossary.NodeStatus.OK:
                self.removed.append(node)
                root.node_list.pop(i)
            else:
                root.node_list[i] = self.check(node)
        return root

    def parse(self, amr: str) -> Node:
        self.reinitialise()
        amr = self.strip_accents(amr)
        root = self.get_nodes(Glossary.TOP, self.string2array(amr))

        if root is not None:
            Parser.endless = 0
            Parser.endless2 = 0
            self.root_copy = root.get_copy(parser_nodes_copy=self.nodes_copy)
            if Parser.endless > Glossary.ENDLESS:
                self.root_copy = Node("Error", "Recursive")
                return root
        else:
            return Node("Error", "Root_is_None")

        root = self.check_missing_instances(root)

        # metodo per controllo multi sentence
        root = self.multi_sentence(root)

        # richiama il metodo che effettua la traduzione delle relazioni e dei valori
        root = self.fred_translate(root)

        # richiama il metodo che disambigua i verbi ed esplicita i ruoli dei predicati anonimi
        root = self.verbs_elaboration(root)

        # verifica la necessità di inserire il nodo speciale TOPIC
        root = self.topic(root)

        # verifica e tenta correzione errori residui
        root = self.residual(root)

        # AMR INTEGRATION
        root = self.logic_triples_integration(root)
        return root

    def fred_translate(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        elif len(root.node_list) == 0:
            self.set_equals(root)  # verificare comportamento
            return root

        if Parser.endless > Glossary.ENDLESS:
            return root

        for node in self.nodes:
            if node.get_instance() is not None:
                self.vars.append(node.var)

        root = self.dom_verify(root)

        # verifica ops
        root = self.control_ops(root)

        # verifica punti elenco
        root = self.li_verify(root)

        # verifica inversi
        root = self.inverse_checker(root)

        # verifica :mod
        root = self.mod_verify(root)

        # Elaborazione della lista dei nodi contenuti nel nodo attualmente in lavorazione
        root = self.list_elaboration(root)

        root = self.add_parent_list(root)

        # elaborazione del nodo figlio denominato instance in amr
        root = self.instance_elaboration(root)

        return root

    def check_missing_instances(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        if root.relation != Glossary.INSTANCE and root.get_instance() is None:
            for n in self.nodes:
                if n.var == root.var and n.get_instance() is not None:
                    root.make_equals(node=n)
            for i, node in enumerate(root.node_list):
                root.node_list[i] = self.check_missing_instances(node)
        return root

    def multi_sentence(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        if root.get_instance() is not None and root.get_instance().var == Glossary.AMR_MULTI_SENTENCE:
            sentences = root.get_snt()
            new_root = sentences.pop(0)
            new_root.relation = Glossary.TOP
            new_root.parent = None
            new_root.node_list += sentences
            for node in sentences:
                node.parent = new_root
                node.relation = Glossary.TOP
            return new_root
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.multi_sentence(node)
        return root

    def logic_triples_integration(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root

        if root.status != Glossary.NodeStatus.OK:
            return root

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.logic_triples_integration(node)
        vis = False
        obj = root.relation
        for a in Glossary.AMR_INTEGRATION:
            if obj == Glossary.AMR + a[1:] and not a.endswith("_of"):
                rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
                rel.node_list.append(
                    Node(Glossary.PB_GENERICROLE + a[1:], Glossary.OWL_EQUIVALENT_PROPERTY, Glossary.NodeStatus.OK,
                         vis))
                rel.node_list.append(Node(Glossary.OWL_OBJECT_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                rel.node_list.append(
                    Node(Glossary.FS_SCHEMA_SEMANTIC_ROLE, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                root.add(rel)

            elif obj == Glossary.AMR + a[1:] and a.endswith("_of"):
                rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
                rel.node_list.append(
                    Node(Glossary.PB_GENERICROLE + a.substring(1).replace("_of", ""), Glossary.OWL_INVERSE_OF,
                         Glossary.NodeStatus.OK, vis))
                rel.node_list.append(Node(Glossary.OWL_OBJECT_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                rel.node_list.append(
                    Node(Glossary.FS_SCHEMA_SEMANTIC_ROLE, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                root.add(rel)

        if (not obj.startswith(Glossary.FRED)
                and not obj.startswith(Glossary.RDFS)
                and not obj.startswith(Glossary.RDF)
                and not obj.startswith(Glossary.OWL)
                and not obj == Glossary.DUL_HAS_DATA_VALUE
                and not obj == Glossary.DUL_HAS_AMOUNT
                and not obj == Glossary.TOP):

            rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
            root.add(rel)
            rel.node_list.append(Node(Glossary.OWL_OBJECT_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
        elif obj == Glossary.DUL_HAS_DATA_VALUE or obj == Glossary.DUL_HAS_AMOUNT:
            rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
            root.add(rel)
            rel.node_list.append(Node(Glossary.OWL_DATA_TYPE_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))

        return root

    def set_equals(self, root: Node):
        if not isinstance(root, Node):
            return
        for node in self.get_equals(root):
            node.var = root.var

    def get_equals(self, root: Node) -> list[Node]:
        if not isinstance(root, Node):
            return []
        return [node for node in self.nodes if node.__eq__(root)]

    def dom_verify(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        dom = root.get_child(Glossary.AMR_DOMAIN)
        if dom is not None:
            instance = root.get_instance()
            if instance is None:
                instance = self.get_instance_alt(root.get_node_id())
            self.topic_flag = False
            dom.relation = Glossary.TOP
            if dom.get_instance() is None and self.get_instance_alt(dom.get_node_id()) is not None:
                n_var = self.get_instance_alt(dom.get_node_id())
            elif dom.get_instance() is not None:
                n_var = dom.get_instance().var
            else:
                n_var = Glossary.FRED + dom.var.replace(Glossary.LITERAL, "")
            dom.var = n_var
            if instance is None:
                rel = Glossary.DUL_HAS_QUALITY
            elif instance.var in Glossary.ADJECTIVE:
                rel = Glossary.DUL_HAS_QUALITY
                self.treat_instance(root)
                root.var = Glossary.FRED + root.get_instance().var.capitalize()
            else:
                rel = Glossary.RDF_TYPE
                root.var = Glossary.FRED + instance.var.capitalize()
                self.remove_instance(root)
            new_node = root.get_copy(relation=rel)
            dom.node_list.append(new_node)
            self.nodes.append(new_node)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.dom_verify(node)
        return root

    def control_ops(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        ins = root.get_instance()

        if isinstance(ins, Node) and (ins.var != Glossary.OP_NAME or ins.var != Glossary.FRED_MULTIPLE):
            return root
        ops_list = root.get_ops()
        if len(ops_list) > 0:
            for node in ops_list:
                assert isinstance(node, Node)
                if node.get_instance() is None:
                    if re.match(Glossary.NN_INTEGER, node.var):
                        node.relation = Glossary.DUL_HAS_DATA_VALUE
                        if (re.match(Glossary.NN_INTEGER, node.var)
                                and int(node.var) == 1
                                and root.get_child(Glossary.QUANT_HAS_QUANTIFIER) is None
                                and (ins is None or ins.var != Glossary.AMR_VALUE_INTERVAL)):
                            root.add(Node(Glossary.QUANT + Glossary.FRED_MULTIPLE, Glossary.QUANT_HAS_QUANTIFIER,
                                          Glossary.NodeStatus.OK))
                    else:
                        node.relation = Glossary.DUL_ASSOCIATED_WITH
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.control_ops(node)
        return root

    def li_verify(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        if root.relation == Glossary.AMR_LI:
            root.relation = Glossary.TOP
            var = root.parent.var
            new_instance = Node(Glossary.REIFI_HAVE_LI, Glossary.INSTANCE)
            self.nodes.append(new_instance)
            arg1 = Node(root.var, Glossary.AMR_ARG1)
            self.nodes.append(arg1)
            arg2 = Node(var, Glossary.AMR_ARG2)
            self.nodes.append(arg2)
            arg2.make_equals(root.parent)
            root.var = "li_" + str(root.get_node_id())
            root.add(new_instance)
            root.add(arg1)
            root.add(arg2)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.li_verify(node)
        return root

    def inverse_checker(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        inv_nodes = root.get_inverses([])
        if len(inv_nodes) == 0:
            return root
        inv_nodes = root.get_inverses()
        if root.relation == Glossary.TOP and len(inv_nodes) == 1 and root.get_node_id() == 0:
            n = root.get_inverse()
            root.node_list.remove(n)
            root.relation = n.relation[0:-3]
            n.add(root)
            n.relation = Glossary.TOP
            return self.inverse_checker(n)
        else:
            for node in inv_nodes:
                new_node = root.get_copy(relation=node.relation[0:-3])
                if len(node.node_list) == 0 or (len(node.node_list) == 1 and node.get_instance() is not None):
                    ancestor = self.get_verb_ancestor(root)
                    new_parent = ancestor.get_copy(relation=Glossary.DUL_PRECEDES)
                    self.nodes.append(new_parent)
                    new_parent.set_status(Glossary.NodeStatus.AMR)
                    node.add(new_parent)
                self.nodes.append(new_node)
                node.relation = Glossary.TOP
                node.add(new_node)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.inverse_checker(node)
        return root

    def get_verb_ancestor(self, root: Node) -> Node | None:
        node = root
        while node.get_node_id() > 0 and node.parent is not None:
            parent_ins = self.get_instance_alt(node.parent.get_node_id())
            if parent_ins is not None and re.match(Glossary.AMR_VERB2, parent_ins.var):
                return node.parent
            elif node.parent is not None:
                node = node.parent
        return node

    def mod_verify(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        flag = True
        instance = self.get_instance_alt(root.get_node_id())
        if isinstance(instance, Node) and len(instance.var) > 3 and re.fullmatch(Glossary.AMR_VERB, instance.var[3:]):
            flag = False

        dom = root.get_child(Glossary.AMR_DOMAIN)
        mods = root.get_children(Glossary.AMR_MOD)

        for mod_node in mods:
            if isinstance(mod_node, Node) and flag:
                if isinstance(mod_node.get_instance(), Node):
                    mod_instance = mod_node.get_instance()
                elif isinstance(self.get_instance_alt(mod_node.get_node_id()), Node):
                    mod_instance = self.get_instance_alt(mod_node.get_node_id())
                else:
                    mod_instance = None
                if (mod_node.get_child(Glossary.AMR_DEGREE) is not None
                        and mod_node.get_child(Glossary.AMR_COMPARED_TO) is not None
                        and mod_instance is not None):
                    # caso :mod + :degree + :compared-to
                    instance.var = mod_instance.var + instance.var.capitalize()
                    self.remove_instance(mod_node)
                    root.node_list.remove(mod_node)
                    root.add_all(mod_node.node_list)
                elif (mod_instance is not None
                      and instance is not None
                      and not self.is_verb(mod_instance.var)
                      and mod_instance != Glossary.DISJUNCT
                      and mod_instance != Glossary.CONJUNCT
                      and mod_node.get_child(Glossary.AMR_NAME) is None):
                    if mod_node.get_instance() is not None:
                        mod_ins = mod_node.get_instance().var
                    else:
                        mod_ins = self.get_instance_alt(mod_node.get_node_id()).var
                    contains = mod_ins in Glossary.ADJECTIVE
                    demonstratives = " " + mod_ins + " " in Glossary.DEMONSTRATIVES
                    if contains:
                        mod_node.relation = Glossary.DUL_HAS_QUALITY
                        mod_node.var = Glossary.FRED + mod_ins.capitalize()
                        self.remove_instance(mod_node)
                    elif demonstratives:
                        mod_node.relation = Glossary.QUANT_HAS_DETERMINER
                        mod_node.var = Glossary.FRED + mod_ins.capitalize()
                        self.remove_instance(mod_node)
                    else:
                        if dom is None:
                            root_ins = instance.var
                            root.var = Glossary.FRED + root_ins.lower() + "_" + str(self.occurrence(root_ins))
                            self.remove_instance(root)
                            mod_node.var = (Glossary.FRED
                                            + mod_ins.replace(Glossary.FRED, "").capitalize()
                                            + root_ins.replace(Glossary.FRED, "").capitalize())
                            self.remove_instance(mod_node)
                            mod_node.relation = Glossary.RDF_TYPE
                            if mod_node.get_child(Glossary.RDFS_SUBCLASS_OF) is None:
                                mod_node.add(Node(Glossary.FRED + root_ins.replace(Glossary.FRED, "").capitalize(),
                                                  Glossary.RDFS_SUBCLASS_OF))
                            mod_node.add(Node(Glossary.FRED + (mod_ins.replace(Glossary.FRED, "")).capitalize(),
                                              Glossary.DUL_ASSOCIATED_WITH))
                        else:
                            root_ins = instance.var
                            root.var = (Glossary.FRED + mod_ins.replace(Glossary.FRED, "").capitalize()
                                        + root_ins.replace(Glossary.FRED, ""))
                            instance.var = root.var
                            self.remove_instance(root)
                            mod_node.var = Glossary.FRED + mod_ins.replace(Glossary.FRED, "").capitalize()
                            mod_node.relation = Glossary.DUL_ASSOCIATED_WITH
                            self.remove_instance(mod_node)
                            if root.get_child(Glossary.RDFS_SUBCLASS_OF) is None:
                                root.add(Node(Glossary.FRED + root_ins.replace(Glossary.FRED, "").capitalize(),
                                              Glossary.RDFS_SUBCLASS_OF))
                    mod_node.set_status(Glossary.NodeStatus.OK)
            elif mod_node is not None and not flag:
                if mod_node.get_instance() is not None:
                    mod_ins = mod_node.get_instance().var
                else:
                    mod_ins = self.get_instance_alt(mod_node.get_node_id()).var
                contains = mod_ins in Glossary.ADJECTIVE
                demonstratives = " " + mod_ins + " " in Glossary.DEMONSTRATIVES
                if contains:
                    mod_node.relation = Glossary.DUL_HAS_QUALITY
                    mod_node.var = Glossary.FRED + mod_ins.capitalize()
                    self.remove_instance(mod_node)
                elif demonstratives:
                    mod_node.relation = Glossary.QUANT_HAS_DETERMINER
                    mod_node.var = Glossary.FRED + mod_ins.capitalize()
                    self.remove_instance(mod_node)
                else:
                    mod_node.var = Glossary.FRED + mod_ins.replace(Glossary.FRED, "").capitalize()
                    mod_node.relation = Glossary.DUL_ASSOCIATED_WITH
                    self.remove_instance(mod_node)
                mod_node.set_status(Glossary.NodeStatus.OK)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.mod_verify(node)

        return root

    def list_elaboration(self, root: Node) -> Node:
        if not isinstance(root, Node) or len(root.node_list) == 0:
            return root

        root = self.root_elaboration(root)
        root = self.date_entity(root)
        root = self.prep_control(root)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.prep_control(node)

            if node.relation == Glossary.AMR_WIKIDATA:
                if node.var == Glossary.AMR_MINUS:
                    node.relation = ""
                    node.status = Glossary.NodeStatus.REMOVE
                else:
                    node.relation = Glossary.OWL_SAME_AS
                    node.var = Glossary.WIKIDATA + node.var
                    node.status = Glossary.NodeStatus.OK

            if node.relation == Glossary.PREP_SUBSTITUTION:
                node.status = Glossary.NodeStatus.REMOVE
                self.to_add += node.node_list

            if node.relation == Glossary.AMR_POLARITY_OF:
                node.relation = Glossary.AMR + Glossary.AMR_POLARITY_OF[1:]

            if (node.relation == Glossary.AMR_DOMAIN and node.get_instance() is not None
                    and " " + node.get_instance().var + " " in Glossary.DEMONSTRATIVES):
                self.topic_flag = False
                node.relation = Glossary.QUANT_HAS_DETERMINER
                node.var = Glossary.FRED + node.get_instance().var.capitalize()
                self.remove_instance(node)
                node.status = Glossary.NodeStatus.OK

            node_instance = node.get_instance()

            # "OR" and "AND" cases with ":OPS"
            if node_instance is not None and (node_instance.var == Glossary.OR or node_instance.var == Glossary.AND):
                if node_instance.var == Glossary.AND:
                    node_instance.var = Glossary.CONJUNCT
                else:
                    node_instance.var = Glossary.DISJUNCT
                ops = node.get_ops()
                for n in ops:
                    n.relation = Glossary.DUL_HAS_MEMBER

            # "date-interval" case with ":op" list
            if node_instance is not None and node_instance.var == Glossary.AMR_DATE_INTERVAL:
                ops = node.get_ops()
                for n in ops:
                    n.relation = Glossary.DUL_HAS_MEMBER

            # special cases with personal pronouns and demonstrative adjectives
            if node.var in Glossary.PERSON:
                node.var = Glossary.FRED_PERSON
                # self.set_equals(root)
                root.prefix = True

            if node.relation == Glossary.AMR_NAME:
                root.prefix = True
                if root.get_poss() is not None and root.get_instance() is not None:
                    root.get_poss().relation = root.get_instance().var.replace(Glossary.FRED, "") + Glossary.OF

            if (node.relation == Glossary.AMR_NAME and node_instance is not None
                    and node_instance.var == Glossary.OP_NAME
                    and len(node.get_ops()) > 0
                    and not self.check_for_amr_instances(root)):
                ops = node.get_ops()
                name = ""
                for n in ops:
                    name += Glossary.OP_JOINER + n.var
                    node.node_list.remove(n)
                name = Glossary.LITERAL + name[1:].replace(Glossary.LITERAL, "")
                node.var = name
                node.relation = Glossary.SCHEMA + Glossary.OP_NAME
                self.treat_instance(node)
            elif (node.relation == Glossary.AMR_NAME and node_instance is not None
                  and node_instance.var == Glossary.OP_NAME
                  and len(node.get_ops()) > 0
                  and self.check_for_amr_instances(root)):
                ops = node.get_ops()
                name = ""
                for n in ops:
                    name += Glossary.OP_JOINER + n.var
                    node.node_list.remove(n)
                name = Glossary.LITERAL + name[1:].replace(Glossary.LITERAL, "")
                node.var = name
                node.relation = Glossary.SCHEMA + Glossary.OP_NAME
                self.treat_instance(node)
                self.remove_instance(node)
            elif (node_instance is not None and node_instance.var == Glossary.OP_NAME
                  and len(node.get_ops()) > 0
                  and not self.check_for_amr_instances(root)):
                ops = node.get_ops()
                name = ""
                for n in ops:
                    name += Glossary.OP_JOINER + n.var
                    node.node_list.remove(n)
                name = Glossary.LITERAL + name[1:].replace(Glossary.LITERAL, "")
                node.var = name
                self.treat_instance(node)

            if node.relation == Glossary.AMR_WIKI:
                if node.var == Glossary.AMR_MINUS:
                    node.status = Glossary.NodeStatus.REMOVE
                else:
                    node.relation = Glossary.OWL_SAME_AS
                    node.var = Glossary.DBPEDIA + node.var
                    node.status = Glossary.NodeStatus.OK

            elif node.relation == Glossary.AMR_MODE and (node.var == Glossary.AMR_IMPERATIVE
                                                         or node.var == Glossary.AMR_EXPRESSIVE
                                                         or node.var == Glossary.AMR_INTERROGATIVE):
                node.relation = Glossary.AMR + node.relation[1:]
                node.var = Glossary.AMR + node.var.replace(":", "")

            elif node.relation == Glossary.AMR_POLITE:
                if node.var != Glossary.AMR_PLUS:
                    node.add(Node(Glossary.BOXING_FALSE, Glossary.BOXING_HAS_TRUTH_VALUE, Glossary.NodeStatus.OK))
                node.var = Glossary.AMR + node.relation[1:]
                node.relation = Glossary.BOXING_HAS_MODALITY
                node.add(Node(Glossary.DUL_HAS_QUALITY, Glossary.RDFS_SUB_PROPERTY_OF, Glossary.NodeStatus.OK))

            elif (node.relation == Glossary.AMR_POLARITY
                  and node_instance is not None
                  and node_instance.var == Glossary.AMR_UNKNOWN):
                node.relation = Glossary.BOXING_HAS_TRUTH_VALUE
                node.var = Glossary.BOXING_UNKNOWN
                self.remove_instance(node)

            elif node_instance is not None and node_instance.var == Glossary.AMR_UNKNOWN:
                node.var = Glossary.OWL_THING
                self.remove_instance(node)
                if node.relation == Glossary.AMR_QUANT:
                    node.relation = Glossary.AMR + Glossary.AMR_QUANT[1:]

            elif " " + node.var + " " in Glossary.MALE:
                node.var = Glossary.FRED_MALE
                self.set_equals(root)

            elif " " + node.var + " " in Glossary.FEMALE:
                node.var = Glossary.FRED_FEMALE
                self.set_equals(root)

            elif " " + node.var + " " in Glossary.THING:
                node.var = Glossary.FRED_NEUTER
                node.add(Node(Glossary.OWL_THING, Glossary.RDF_TYPE, Glossary.NodeStatus.OK))
                self.set_equals(root)
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == Glossary.AMR_POSS and self.get_instance_alt(root.get_node_id()) is not None:
                node.relation = (Glossary.FRED
                                 + self.get_instance_alt(root.get_node_id()).var.replace(Glossary.FRED, "")
                                 + Glossary.OF)
                node.set_status(Glossary.NodeStatus.OK)

            elif ((node.relation == Glossary.AMR_QUANT or node.relation == Glossary.AMR_FREQUENCY)
                  and re.match(Glossary.NN_INTEGER, node.var) and node_instance is None):
                node.relation = Glossary.DUL_HAS_DATA_VALUE
                if ((re.match(Glossary.NN_INTEGER, node.var) and not int(node.var) == 1)
                        or not re.match(Glossary.NN_INTEGER, node.var)):
                    self.to_add.append(Node(Glossary.QUANT + Glossary.FRED_MULTIPLE,
                                            Glossary.QUANT_HAS_QUANTIFIER,
                                            Glossary.NodeStatus.OK))
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == (Glossary.AMR_QUANT and node_instance is not None
                                   and re.match(Glossary.AMR_QUANTITY, node_instance.var)):
                ops = node.get_ops()
                for n in ops:
                    node.node_list.remove(n)
                    n.relation = Glossary.DUL_HAS_DATA_VALUE
                    self.to_add.append(n)
                    n.set_status(Glossary.NodeStatus.OK)
                node.relation = Glossary.QUANT_HAS_QUANTIFIER
                if node_instance.var == Glossary.FRED_MULTIPLE:
                    node.var = Glossary.QUANT + Glossary.FRED_MULTIPLE
                    self.remove_instance(node)
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == Glossary.AMR_QUANT_OF and node_instance is not None:
                node.relation = Glossary.FRED + self.get_instance_alt(root.get_node_id()).var + Glossary.OF
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == Glossary.AMR_AGE and root.get_instance() is not None and node_instance is None:
                age = node.var
                node.relation = Glossary.TOP
                node.var = Glossary.NEW_VAR + str(self.occurrence(Glossary.NEW_VAR))
                node.add(Node(Glossary.AGE_01, Glossary.INSTANCE))
                n1 = root.get_copy(relation=Glossary.AMR_ARG1)
                self.nodes.append(n1)
                node.add(n1)
                node.add(Node(age, Glossary.AMR_ARG2))
                root.node_list[i] = self.list_elaboration(node)

            elif node.relation == Glossary.AMR_AGE and root.get_instance() is not None and node_instance is not None:
                node.relation = Glossary.TOP
                n1 = root.get_copy(relation=Glossary.AMR_ARG1)
                self.nodes.append(n1)
                new_age_node = Node(Glossary.NEW_VAR + str(self.occurrence(Glossary.NEW_VAR)), Glossary.AMR_ARG2)
                self.nodes.append(new_age_node)
                new_age_node.add_all(node.node_list)
                node.node_list = []
                node.add(n1)
                node.var = Glossary.NEW_VAR + str(self.occurrence(Glossary.NEW_VAR))
                node.add(Node(Glossary.AGE_01, Glossary.INSTANCE))
                node.add(new_age_node)
                root.node_list[i] = self.list_elaboration(node)

            elif node.relation == (Glossary.AMR_DEGREE and node_instance is not None
                                   and not self.is_verb(node_instance.var)):
                node.var = Glossary.FRED + node_instance.var.capitalize()
                self.remove_instance(node)

            elif node.relation == (Glossary.AMR_MANNER and node_instance is not None
                                   and not self.is_verb(node_instance.var)):
                if re.match(Glossary.AMR_VERB2, node_instance.var) or len(self.manner_adverb(node_instance.var)) > 0:
                    if (re.match(Glossary.AMR_VERB2, node_instance.var) and len(
                            self.manner_adverb(node_instance.var[0:-3]))) > 0:
                        node.var = Glossary.FRED + self.manner_adverb(node_instance.var[0:-3]).capitalize()
                    elif len(self.manner_adverb(node_instance.var)) > 0:
                        node.var = Glossary.FRED + self.manner_adverb(node_instance.var).capitalize()
                    else:
                        node.var = Glossary.FRED + node_instance.var[0:-3].capitalize()
                    self.remove_instance(node)
                else:
                    node.relation = Glossary.AMR + Glossary.AMR_MANNER[1:]

            elif (node.relation == Glossary.AMR_MANNER and node_instance is not None and root.get_instance() is not None
                  and self.is_verb(node_instance.var)):
                node.relation = Glossary.FRED + root.get_instance().var[:-3] + Glossary.BY

            elif node.relation.startswith(Glossary.AMR_PREP):
                node.relation = node.relation.replace(Glossary.AMR_PREP, Glossary.FRED)

            elif (node.relation == Glossary.AMR_PART_OF or node.relation == Glossary.AMR_CONSIST_OF
                  and node_instance is not None):
                node.relation = node.relation.replace(Glossary.AMR_RELATION_BEGIN, Glossary.AMR)

            elif node.relation == Glossary.AMR_EXTENT and node_instance is not None:
                node.var = Glossary.FRED + node_instance.var.capitalize()
                self.remove_instance(node)

            if node.relation == Glossary.AMR_VALUE and node_instance is None:
                if re.match(Glossary.NN_INTEGER2, node.var) or re.match(Glossary.NN_INTEGER, node.var):
                    node.relation = Glossary.DUL_HAS_DATA_VALUE
                else:
                    node.relation = Glossary.DUL_HAS_QUALITY
                    node.var = Glossary.FRED + node.var.capitalize()

            if node.relation == Glossary.AMR_CONJ_AS_IF:
                node.relation = Glossary.FRED_AS_IF
                node.set_status(Glossary.NodeStatus.OK)

            if node.relation == Glossary.AMR_CONDITION:
                node.relation = Glossary.DUL_HAS_PRECONDITION

            if node.status != Glossary.NodeStatus.REMOVE:
                for j, relation in enumerate(Glossary.AMR_RELATIONS):
                    if node.relation == relation and re.match(Glossary.AMR_VARS[j], node.var):
                        if len(Glossary.FRED_RELATIONS[j]) > 0:
                            node.relation = Glossary.FRED_RELATIONS[j]
                        if len(Glossary.FRED_VARS[j]) > 0:
                            node.var = Glossary.FRED_VARS[j]
                    node.set_status(Glossary.NodeStatus.OK)

            ops = node.get_ops()
            if len(ops) > 0:
                for n1 in ops:
                    node.node_list.remove(n1)
                    n1.relation = node.relation
                    self.to_add.append(n1)
                node.relation = Glossary.DUL_ASSOCIATED_WITH
                new_node = Node("", "")
                new_node.substitute(node)
                node.set_status(Glossary.NodeStatus.REMOVE)
                self.nodes.append(new_node)
                ops[0].add(new_node)

            if node.status == Glossary.NodeStatus.REMOVE:
                self.removed.append(node)

            if node.relation.startswith(Glossary.AMR_RELATION_BEGIN) and node.status != Glossary.NodeStatus.REMOVE:
                node.set_status(Glossary.NodeStatus.AMR)
            elif node.status != Glossary.NodeStatus.REMOVE:
                node.set_status(Glossary.NodeStatus.OK)

        root.node_list[:] = [node for node in root.node_list if node.status != Glossary.NodeStatus.REMOVE]

        if len(self.to_add) > 0:
            root.add_all(self.to_add)
            self.to_add = []
            root = self.list_elaboration(root)

        if root.relation == Glossary.TOP and len(root.get_ops()) > 0:
            ops = root.get_ops()
            for op in ops:
                root.node_list.remove(op)
            new_root = Node("", "")
            new_root.substitute(root)
            new_root.relation = Glossary.DUL_ASSOCIATED_WITH
            self.nodes.append(new_root)
            root.substitute(ops[0])
            root.add(new_root)
            root.relation = Glossary.TOP
            for op in ops:
                op.relation = Glossary.TOP
                if not root.__eq__(op):
                    root.add(op)

            if root.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                root.set_status(Glossary.NodeStatus.AMR)
            else:
                root.set_status(Glossary.NodeStatus.OK)

        if Parser.endless2 > Glossary.ENDLESS2:
            return root

        for i, node in enumerate(root.node_list):
            Parser.endless2 += 1
            root.node_list[i] = self.list_elaboration(node)

        return root

    def add_parent_list(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        to_add = root.get_nodes_with_parent_list_not_empty()
        if len(to_add) != 0:
            for node in to_add:
                for node_1 in node.parent_list:
                    flag = False
                    for node_2 in root.node_list:
                        if node_1.relation == node_2.relation and node_1.var == node_2.var:
                            flag = True
                    if not flag:
                        root.node_list.append(node_1)
                root.node_list.remove(node)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.add_parent_list(node)
        return root

    def instance_elaboration(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        if root.status == Glossary.NodeStatus.OK and root.relation.startswith(
                Glossary.AMR_RELATION_BEGIN) and root.relation != Glossary.TOP:
            root.set_status(Glossary.NodeStatus.AMR)
            return root

        if root.status != Glossary.NodeStatus.OK and root.relation.startswith(
                Glossary.AMR_RELATION_BEGIN) and root.relation != Glossary.TOP:
            root.set_status(Glossary.NodeStatus.OK)

        instance = root.get_instance()
        if isinstance(instance, Node):
            if len(instance.var) > 3 and re.match(Glossary.AMR_VERB, instance.var[-3:]):
                if self.is_verb(instance.var):
                    root.node_type = Glossary.NodeType.VERB
                    self.topic_flag = False
                    instance.add(Node(Glossary.DUL_EVENT, Glossary.RDFS_SUBCLASS_OF, Glossary.NodeStatus.OK))
                if root.status == Glossary.NodeStatus.OK:
                    root.node_type = Glossary.NodeType.VERB
                    self.topic_flag = False

                root.var = Glossary.FRED + instance.var[0:-3] + "_" + str(self.occurrence(instance.var[0:-3]))
                instance.relation = Glossary.RDF_TYPE
                root.verb = Glossary.ID + instance.var.replace('-', '.')
                self.args(root)
                instance.var = Glossary.PB_ROLESET + instance.var

                if not instance.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    instance.status = Glossary.NodeStatus.OK
                else:
                    instance.status = Glossary.NodeStatus.AMR

                if not root.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    root.status = Glossary.NodeStatus.OK
                else:
                    root.status = Glossary.NodeStatus.AMR
            else:
                root = self.other_instance_elaboration(root)
                if not root.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    root.status = Glossary.NodeStatus.OK
                else:
                    root.status = Glossary.NodeStatus.AMR

            for node in self.nodes:
                if root.__eq__(node):
                    node.var = root.var

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.instance_elaboration(node)

        return root

    def verbs_elaboration(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        lemma = root.verb
        if root.node_type == Glossary.NodeType.VERB:
            pb = Propbank.get_propbank()
            lemma2 = lemma[3:].replace(".", "-")
            roles = pb.frame_find(Glossary.PB_ROLESET + lemma2, Glossary.PropbankFrameFields.PB_Frame)
            if len(roles) > 0:
                label = roles[0][Glossary.PropbankFrameFields.PB_FrameLabel.value]
                if len(label) > 0 and isinstance(root.get_child(Glossary.RDF_TYPE), Node):
                    root.get_child(Glossary.RDF_TYPE).add(Node(label, Glossary.RDFS_LABEL, Glossary.NodeStatus.OK))
                new_nodes_vars = []
                for line in roles:
                    fn_frame = line[Glossary.PropbankFrameFields.FN_Frame.value]
                    if fn_frame is not None and len(fn_frame) > 0 and fn_frame not in new_nodes_vars:
                        new_nodes_vars.append(fn_frame)
                    va_frame = line[Glossary.PropbankFrameFields.VA_Frame.value]
                    if va_frame is not None and len(va_frame) > 0 and va_frame not in new_nodes_vars:
                        new_nodes_vars.append(va_frame)

                type_node = root.get_child(Glossary.RDF_TYPE)
                if isinstance(type_node, Node):
                    for var in new_nodes_vars:
                        new_node = Node(var, Glossary.FS_SCHEMA_SUBSUMED_UNDER, Glossary.NodeStatus.OK)
                        type_node.add(new_node)
                        new_node.visibility = False

                # search for roles
                for node in root.get_args():
                    if isinstance(node, Node):
                        r = Glossary.PB_ROLESET + lemma2

                        pb_roles = pb.role_find(r,
                                                Glossary.PropbankRoleFields.PB_Frame,
                                                Glossary.PB_SCHEMA + node.relation[1:].upper(),
                                                Glossary.PropbankRoleFields.PB_ARG)

                        if (len(pb_roles) > 0
                                and pb_roles[0][Glossary.PropbankRoleFields.PB_Role.value] is not None
                                and len(pb_roles[0][Glossary.PropbankRoleFields.PB_Role.value]) > 0):
                            node.relation = pb_roles[0][Glossary.PropbankRoleFields.PB_Role.value]
                        node.status = Glossary.NodeStatus.OK

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.verbs_elaboration(node)
        return root

    def topic(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        if self.topic_flag:
            root.add(Node(Glossary.FRED_TOPIC, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK))
        return root

    def residual(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        # print(root)
        if Glossary.LITERAL in root.var:
            root.var = root.var.replace(Glossary.LITERAL, "")
            root.set_status(Glossary.NodeStatus.OK)

        if Glossary.NON_LITERAL not in root.var and len(root.node_list) == 1:
            var = root.var
            root_id = root.get_node_id()
            child = root.node_list[0]
            if Glossary.NON_LITERAL in child.var and child.relation == Glossary.DUL_ASSOCIATED_WITH:
                root.var = child.var
                root.add_all(child.node_list)
                root.make_equals(child)
                child.make_equals(node_id=root_id)
                child.node_list = []
                child.var = var

        if Glossary.FRED + Glossary.LITERAL2 in root.var:
            root.var = root.var.replace(Glossary.FRED + Glossary.LITERAL2, "")
            root.set_status(Glossary.NodeStatus.OK)

        if Glossary.FRED in root.var or Glossary.AMR in root.var:
            temp = root.var.replace(Glossary.FRED, "").replace(Glossary.AMR, "")
            temp = self.disambiguation(temp)
            root.var = temp

        if "fred:Fred:" in root.var:
            root.var = root.var.replace("fred:Fred:", "")
            root.var = Glossary.FRED + root.var.capitalize()

        if re.match(Glossary.AMR_VERB2, root.var) and root.status != Glossary.NodeStatus.OK and len(root.var) > 3:
            root.add(Node(Glossary.DUL_EVENT, Glossary.RDFS_SUBCLASS_OF, Glossary.NodeStatus.OK))
            args = root.get_args()
            if Glossary.NON_LITERAL in root.var:
                verb = root.var.split(Glossary.NON_LITERAL)[1]
            else:
                verb = root.var

            for arg in args:
                arg.verb = verb
            root.var = root.var[0:-3]
            root.node_type = Glossary.NodeType.VERB

        elif re.match(Glossary.AMR_VERB2, root.var) and root.status != Glossary.NodeStatus.OK:
            if Glossary.NON_LITERAL in root.var:
                new_var = root.var.split(Glossary.NON_LITERAL)[1].lower()
            else:
                new_var = root.var

            root.malformed = True
            root.add(Node(Glossary.FRED + new_var[0:-3].capitalize(), Glossary.RDF_TYPE, Glossary.NodeStatus.OK))
            root.var = Glossary.FRED + new_var[0:-3] + "_" + str(self.occurrence(new_var[0:-3]))
            self.set_equals(root)

        if re.match(Glossary.AMR_ARG, root.relation):
            root.relation = Glossary.VN_ROLE_PREDICATE
            root.malformed = True
            root.set_status(Glossary.NodeStatus.OK)

        if root.relation == Glossary.AMR_COMPARED_TO:
            new_relation = Glossary.AMR + Glossary.AMR_COMPARED_TO
            root.relation = new_relation
            root.set_status(Glossary.NodeStatus.OK)

        if (root.relation == Glossary.AMR_MODE and (root.var == Glossary.AMR_IMPERATIVE
                                                    or root.var == Glossary.AMR_EXPRESSIVE
                                                    or root.var == Glossary.AMR_INTERROGATIVE)):
            root.relation = Glossary.AMR + root.relation[1:]
            root.var = Glossary.AMR + root.var.replace(":", "")
            root.set_status(Glossary.NodeStatus.OK)

        if root.relation == Glossary.AMR_CONSIST_OF or root.relation == Glossary.AMR_UNIT:
            root.relation = root.relation.replace(":", Glossary.AMR)
            root.set_status(Glossary.NodeStatus.OK)

        if root.relation.startswith(Glossary.NON_LITERAL):
            root.relation = root.relation.replace(Glossary.NON_LITERAL, Glossary.AMR)
            if (Glossary.NON_LITERAL not in root.var and root.status != Glossary.NodeStatus.OK
                    and Glossary.FRED not in root.var):
                root.var = Glossary.FRED + root.var.capitalize()
            root.set_status(Glossary.NodeStatus.OK)

        if root.var == Glossary.AMR_MINUS and root.relation == Glossary.PBLR_POLARITY:
            root.var = Glossary.FRED + "Negative"

        for node in root.node_list:
            if Glossary.NON_LITERAL not in node.var and node.var in self.vars:
                node.var = Glossary.FRED + "malformed_amr/" + node.var
                node.malformed = True

        root.node_list[:] = [n for n in root.node_list if n.status != Glossary.NodeStatus.REMOVE]

        if Glossary.NON_LITERAL not in root.var and re.match(Glossary.AMR_VAR, root.var):
            root.var = Glossary.FRED + "Undefined"
            root.malformed = True

        if root.var.count(Glossary.NON_LITERAL) > 1:
            root.var = ":".join(root.var.split(Glossary.NON_LITERAL)[-2:])

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.residual(node)

        return root

    def get_instance_alt(self, node_id) -> Node | None:
        for node in self.nodes_copy:
            if node.get_node_id() == node_id and node.get_instance() is not None:
                return node.get_instance()
        return None

    def treat_instance(self, root: Node):
        if not isinstance(root, Node):
            return
        for node in self.get_equals(root):
            node.var = root.var
        if root.get_instance() is not None:
            root.get_instance().status = Glossary.NodeStatus.REMOVE

    def remove_instance(self, root: Node):
        if not isinstance(root, Node):
            return
        for node in self.get_equals(root):
            node.var = root.var
        if root.get_instance() is not None:
            root.node_list.remove(root.get_instance())

    @staticmethod
    def is_verb(var, node_list=None) -> bool:
        prb = Propbank.get_propbank()
        if node_list is None and isinstance(var, str):
            result = prb.frame_find(Glossary.PB_ROLESET + var, Glossary.PropbankFrameFields.PB_Frame)
            return result is not None and len(result) > 0
        elif isinstance(var, str) and isinstance(node_list, list):
            result = prb.list_find(var, node_list)
            return result is not None and len(result) > 0

    def occurrence(self, word) -> int:
        occurrence_num = 1
        for couple in self.couples:
            if word == couple.get_word():
                occurrence_num += couple.get_occurrence()
                couple.set_occurrence(occurrence_num)
        if occurrence_num == 1:
            self.couples.append(Couple(1, word))
        return occurrence_num

    @staticmethod
    def args(root: Node):
        if not isinstance(root, Node):
            return root
        for node in root.node_list:
            if re.match(Glossary.AMR_ARG, node.relation):
                node.verb = root.verb

    def other_instance_elaboration(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        instance = root.get_instance()
        if not isinstance(instance, Node):
            return root

        n_var = Glossary.FRED + instance.var + "_" + str(self.occurrence(instance.var))
        for node in self.get_equals(root):
            ins = node.get_instance()
            if isinstance(ins, Node):
                node.var = n_var
                ins.relation = Glossary.RDF_TYPE
                flag = True
                if instance.var in Glossary.SPECIAL_INSTANCES:
                    ins.var = (Glossary.SPECIAL_INSTANCES_PREFIX[Glossary.SPECIAL_INSTANCES.index(instance.var)]
                               + instance.var.capitalize())
                    flag = False

                if instance.var in Glossary.AMR_INSTANCES and root.prefix:
                    ins.var = Glossary.AMR + instance.var.capitalize()
                    flag = False

                if instance.var in Glossary.AMR_ALWAYS_INSTANCES:
                    ins.var = Glossary.AMR + instance.var.capitalize()
                    flag = False

                if flag:
                    ins.var = Glossary.FRED + instance.var.capitalize()

                if ins.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    ins.status = Glossary.NodeStatus.OK
            else:
                node.var = n_var
        return root

    def root_elaboration(self, root: Node) -> Node:
        instance = self.get_instance_alt(root.get_node_id())
        root_instance = root.get_instance()

        if root_instance is not None and (root_instance.var == Glossary.AND or root_instance == Glossary.OR):
            if root_instance.var == Glossary.AND:
                root_instance.var = Glossary.CONJUNCT
            else:
                root_instance.var = Glossary.DISJUNCT
            ops = root.get_ops()
            for n in ops:
                n.relation = Glossary.DUL_HAS_MEMBER

        if instance is None:
            return root

        if root.get_child(Glossary.AMR_CONCESSION) is not None:
            concession = root.get_child(Glossary.AMR_CONCESSION)
            condition = root.get_child(Glossary.AMR_CONDITION)
            swap = Node("", "")

            if (concession.get_instance() is not None and concession.get_instance().var == Glossary.EVEN_IF
                    and concession.get_child(Glossary.AMR_OP1) is not None):
                root.node_list.remove(concession)
                op1 = concession.get_child(Glossary.AMR_OP1)
                modality = Node(Glossary.BOXING_NECESSARY, Glossary.BOXING_HAS_MODALITY, Glossary.NodeStatus.OK)
                quality = Node(Glossary.FRED_EVEN, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK)
                root.add(modality)
                op1.add(modality)
                swap.substitute(root)
                root.substitute(op1)
                root.relation = swap.relation
                swap.relation = Glossary.FRED_ENTAILS
                swap.add(quality)
                root.add(swap)

            if (concession.get_instance() is not None and concession.get_instance().var == Glossary.EVEN_WHEN
                    and concession.get_child(Glossary.AMR_OP1) is not None):
                root.node_list.remove(concession)
                op1 = concession.get_child(Glossary.AMR_OP1)
                quality = Node(Glossary.FRED_EVEN, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK)
                op1.relation = Glossary.FRED_WHEN
                root.add(quality)
                root.add(op1)

            if condition is not None and condition.get_instance() is not None:
                root.node_list.remove(condition)
                modality = Node(Glossary.BOXING_NECESSARY, Glossary.BOXING_HAS_MODALITY, Glossary.NodeStatus.OK)
                root.add(modality)
                condition.add(modality)
                swap.substitute(root)
                root.substitute(condition)
                root.relation = swap.relation
                swap.relation = Glossary.FRED_ENTAILS
                root.add(swap)

        if instance.var == Glossary.SUM_OF or instance.var == Glossary.PRODUCT_OF:
            if instance.var == Glossary.SUM_OF:
                instance.var = Glossary.SUM
                for op in root.get_ops():
                    op.relation = Glossary.FRED + Glossary.SUM + Glossary.OF
            else:
                instance.var = Glossary.PRODUCT
                for op in root.get_ops():
                    op.relation = Glossary.FRED + Glossary.PRODUCT + Glossary.OF

        if instance.var == Glossary.AMR_RELATIVE_POSITION:
            if (root.get_child(Glossary.AMR_DIRECTION) is not None and root.get_child(Glossary.AMR_OP1) is not None
                    and root.get_child(Glossary.AMR_QUANT) is not None
                    and root.get_child(Glossary.AMR_QUANT).get_instance() is not None):
                op1 = self.get_original(root.get_child(Glossary.AMR_OP1))
                root.node_list.remove(op1)
                direction = self.get_original(root.get_child(Glossary.AMR_DIRECTION))
                op1.relation = Glossary.FRED + direction.get_instance().var + Glossary.OF
                direction.add(op1)
                quant = root.get_child(Glossary.AMR_QUANT)
                root.get_instance().var = quant.get_instance().var.replace(Glossary.QUANTITY, "")

        if len(instance.var) > 3 and re.match(Glossary.AMR_VERB, instance.var[-3:]) and not self.is_verb(
                instance.var) and len(root.get_args()) == 1:
            self.topic_flag = False
            arg = root.get_args()[0]
            root.node_list.remove(arg)
            if root.get_child(Glossary.AMR_DEGREE) is not None and root.get_child(
                    Glossary.AMR_DEGREE).get_instance() is not None:
                instance.var = root.get_child(
                    Glossary.AMR_DEGREE).get_instance().var.capitalize() + instance.var.capitalize()
                root.node_list.remove(root.get_child(Glossary.AMR_DEGREE))

            parent_id = root.get_node_id()
            arg_id = arg.get_node_id()
            parent_var = instance.var[0:-3]
            if arg.get_instance() is not None:
                instance.var = arg.get_instance().var
                self.remove_instance(arg)
            arg.make_equals(node_id=parent_id)
            arg.relation = Glossary.DUL_HAS_QUALITY
            arg.var = Glossary.FRED + parent_var.replace(Glossary.FRED, "")
            root.add_all(arg.node_list)
            arg.node_list = []
            root.add(arg)
            root.make_equals(node_id=arg_id)
            arg.set_status(Glossary.NodeStatus.OK)

        if (len(instance.var) > 3 and re.match(Glossary.AMR_VERB, instance.var[-3:])
                and not self.is_verb(instance.var, root.get_args())):
            if root.get_child(Glossary.AMR_ARG0) is not None and root.get_child(Glossary.AMR_ARG1) is not None:
                root.get_child(Glossary.AMR_ARG0).relation = Glossary.BOXER_AGENT
                root.get_child(Glossary.AMR_ARG1).relation = Glossary.BOXER_PATIENT
                self.topic_flag = False
            if root.get_child(Glossary.AMR_ARG1) is not None and root.get_child(Glossary.AMR_ARG2) is not None:
                root.get_child(Glossary.AMR_ARG1).relation = Glossary.VN_ROLE_EXPERIENCER
                root.get_child(Glossary.AMR_ARG2).relation = Glossary.VN_ROLE_CAUSE
                self.topic_flag = False

        if (root.get_child(Glossary.AMR_SCALE) is not None
                and root.get_child(Glossary.AMR_SCALE).get_instance() is not None):
            scale = root.get_child(Glossary.AMR_SCALE)
            scale.relation = Glossary.FRED_ON
            scale.var = scale.get_instance().var.capitalize() + Glossary.SCALE
            self.remove_instance(scale)

        if root.get_child(Glossary.AMR_ORD) is not None:
            ord_node = root.get_child(Glossary.AMR_ORD)
            root.node_list.remove(ord_node)
            self.remove_instance(ord_node)
            root.add_all(ord_node.node_list)
            value = ord_node.get_child(Glossary.AMR_VALUE)
            if value is not None and re.match(Glossary.NN_INTEGER, value.var):
                num = int(value.var)
                ord_num = self.ordinal(num)
                value.relation = Glossary.QUANT_HAS_QUANTIFIER
                value.var = Glossary.QUANT + ord_num

        return root

    def date_entity(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        instance = root.get_instance()
        if len(root.node_list) == 0 or instance is None or instance.var != Glossary.AMR_DATE_ENTITY:
            return root
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_ERA))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_DECADE))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_CENTURY))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_CALENDAR))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_WEEKDAY))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_DAY_PERIOD))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_QUARTER))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_SEASON))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_TIMEZONE))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_YEAR))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_MONTH))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_DAY))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_YEAR2))
        return root

    def date_child_elaboration(self, child: Node):
        if child is not None:
            child.relation = Glossary.AMRB + child.relation[1:]
            child = self.other_instance_elaboration_prefix(child, Glossary.AMRB)
            child.status = Glossary.NodeStatus.OK

    def prep_control(self, root: Node) -> Node:
        if len(root.node_list) == 0 or root.get_instance() is None or len(root.get_ops()) == 0:
            return root
        var = root.get_instance().var.replace(Glossary.FRED, "")
        quality = Node(Glossary.FRED + var.capitalize(), Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK)
        manner = root.get_child(Glossary.AMR_MANNER)
        if manner is not None:
            manner = manner.get_instance()
        go = False
        for prep in Glossary.PREPOSITION:
            if var == prep:
                go = True
                break
        if go:
            for node in root.get_ops():
                node.relation = root.relation
            if manner is not None and len(self.manner_adverb(manner.var)) > 0:
                quality.var = Glossary.FRED + self.manner_adverb(manner.var) + quality.var.capitalize()
                root.node_list.remove(root.get_child(Glossary.AMR_MANNER))
            else:
                quality.var = Glossary.FRED + quality.var.capitalize()
            root.add(quality)
            self.remove_instance(root)
            if root.relation == Glossary.TOP:
                root.relation = Glossary.PREP_SUBSTITUTION
            else:
                first = root.node_list[0]
                root.node_list.remove(first)
                first.add_all(root.node_list)
                root.substitute(first)
        return root

    @staticmethod
    def check_for_amr_instances(root: Node) -> bool:
        if not isinstance(root, Node):
            return False
        instance = root.get_instance()
        if instance is None:
            return False
        for amr_instance in Glossary.AMR_INSTANCES:
            if instance.var == amr_instance and root.prefix:
                return True
        return False

    @staticmethod
    def manner_adverb(var: str) -> str:
        for adv in Glossary.MANNER_ADVERBS:
            if re.match("^" + var + ".*", adv):
                return adv
        return ""

    def other_instance_elaboration_prefix(self, root: Node, prefix: str) -> Node:
        if not isinstance(root, Node):
            return root
        instance = root.get_instance()
        if instance is None:
            return root
        n_var = Glossary.FRED + instance.var + "_" + str(self.occurrence(instance.var))
        for node in self.get_equals(root):
            instance_in_list = node.get_instance()
            if instance_in_list is not None:
                node.var = n_var
                instance_in_list.relation = Glossary.RDF_TYPE
                flag = True
                if instance.var in Glossary.SPECIAL_INSTANCES:
                    instance_in_list.var = Glossary.SPECIAL_INSTANCES_PREFIX[
                                               Glossary.SPECIAL_INSTANCES.index(
                                                   instance.var)] + instance.var.capitalize()
                    flag = False
                if flag:
                    instance_in_list.var = prefix + instance.var.capitalize()
                if not instance_in_list.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    instance_in_list.set_status(Glossary.NodeStatus.OK)
            else:
                node.var = n_var
        return root

    def get_original(self, root: Node) -> Node | None:
        if not isinstance(root, Node):
            return root
        for node in self.nodes:
            if root.__eq__(node) and node.get_instance() is not None:
                return node
        return None

    @staticmethod
    def ordinal(num: int) -> str:
        suffixes = ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"]
        if num == 11 or num == 12 or num == 13:
            return str(num) + "th"
        else:
            return str(num) + suffixes[num % 10]

    @staticmethod
    def disambiguation(var: str) -> str:
        for i, dul in enumerate(Glossary.DULS_CHECK):
            if dul == var.lower():
                return Glossary.DULS[i]
        return Glossary.FRED + var


class RdfWriter:
    def __init__(self):
        self.queue = []
        self.graph: Graph | None = None
        self.not_visible_graph: Graph | None = None
        self.namespace_manager = NamespaceManager(Graph(), bind_namespaces="rdflib")
        self.new_graph()

        for i, name_space in enumerate(Glossary.NAMESPACE):
            self.namespace_manager.bind(Glossary.PREFIX[i][:-1], name_space)

    def new_graph(self):
        self.graph = Graph()
        # for i, name_space in enumerate(Glossary.NAMESPACE):
        #     self.graph.bind(Glossary.PREFIX[i][:-1], name_space)
        self.not_visible_graph = Graph()
        self.graph.namespace_manager = self.namespace_manager
        self.not_visible_graph.namespace_manager = self.namespace_manager

    def get_prefixes(self):
        names = []
        for prefix, namespace in self.graph.namespaces():
            names.append([prefix, namespace])
        return names

    def to_rdf(self, root: Node):
        self.new_graph()
        if not isinstance(root, Node):
            return
        self.queue = []
        self.queue.append(root)
        while len(self.queue) > 0:
            n = self.queue.pop(0)
            for node in n.node_list:
                self.queue.append(node)
            uri = self.get_uri(n.var)

            for n1 in n.node_list:
                if not uri.startswith("http"):
                    break
                s = URIRef(uri)
                if n1.relation != Glossary.TOP:
                    p = URIRef(self.get_uri(n1.relation))
                    if re.match(Glossary.NN_INTEGER2, n1.var):
                        o = Literal(n1.var, datatype=Glossary.NN_INTEGER_NS)
                    elif re.match(Glossary.DATE_SCHEMA, n1.var):
                        o = Literal(n1.var, datatype=Glossary.DATE_SCHEMA_NS)
                    elif re.match(Glossary.TIME_SCHEMA, n1.var):
                        o = Literal(n1.var, datatype=Glossary.TIME_SCHEMA2_NS)
                    elif (n1.relation == Glossary.RDFS_LABEL
                          or re.match(Glossary.NN_RATIONAL, n1.var)
                          or Glossary.AMR_RELATION_BEGIN not in n1.var):
                        o = Literal(n1.var, datatype=Glossary.STRING_SCHEMA_NS)
                    else:
                        o = URIRef(self.get_uri(n1.var))
                    self.graph.add((s, p, o))
                    if not n.visibility or not n1.visibility:
                        self.not_visible_graph.add((s, p, o))

    def serialize(self, rdf_format: Glossary.RdflibMode) -> str:
        if rdf_format.value in Glossary.RDF_MODE:
            return self.graph.serialize(format=rdf_format.value)

    @staticmethod
    def get_uri(var: str) -> str:
        if Glossary.NON_LITERAL not in var:
            return Glossary.FRED_NS + var
        pref = var.split(Glossary.NON_LITERAL)[0] + Glossary.NON_LITERAL
        name = var.split(Glossary.NON_LITERAL)[1]
        if pref in Glossary.PREFIX:
            return Glossary.NAMESPACE[Glossary.PREFIX.index(pref)] + name
        if pref == "_:":
            return var
        return Glossary.FRED_NS + var


class DigraphWriter:

    @staticmethod
    def node_to_digraph(root: Node):
        """
        Returns root Node translated into .dot graphic language
        :param root: Node
        :return: str
        """
        # new_root = check_visibility(root)  # Uncomment if check_visibility is needed
        new_root = root

        digraph = Glossary.DIGRAPH_INI
        digraph += DigraphWriter.to_digraph(new_root)
        return digraph + Glossary.DIGRAPH_END

    @staticmethod
    def to_digraph(root: Node):
        shape = "box"
        if root.malformed:
            shape = "ellipse"
        digraph = f'"{root.var}" [label="{root.var}", shape={shape},'
        if root.var.startswith(Glossary.FRED):
            digraph += ' color="0.5 0.3 0.5"];\n'
        else:
            digraph += ' color="1.0 0.3 0.7"];\n'
        if root.node_list and root.get_tree_status() == 0:
            for a in root.node_list:
                if a.visibility:
                    shape = "ellipse" if a.malformed else "box"
                    digraph += f'"{a.var}" [label="{a.var}", shape={shape},'
                    if a.var.startswith(Glossary.FRED):
                        digraph += ' color="0.5 0.3 0.5"];\n'
                    else:
                        digraph += ' color="1.0 0.3 0.7"];\n'
                    if a.relation.lower() != Glossary.TOP.lower():
                        digraph += f'"{root.var}" -> "{a.var}" [label="{a.relation}"];\n'
                    digraph += DigraphWriter.to_digraph(a)
        return digraph

    @staticmethod
    def to_png(root: Node | Graph, not_visible_graph: Graph | None = None) -> IO | str:
        """
        Returns an image file (png) of the translated root node.
        If Graphviz is not installed returns a String containing root Node translated into .dot graphic language
        :param not_visible_graph: Graph containing not visible triples
        :param root: translated root node or Graph containing triples
        :return: image file (png)
        """
        if isinstance(root, Node):
            digraph = DigraphWriter.node_to_digraph(root)
        elif isinstance(root, Graph) and isinstance(not_visible_graph, Graph):
            digraph = DigraphWriter.graph_to_digraph(root, not_visible_graph)
            print("here")
        else:
            return ""
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
            tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            with open(tmp.name, 'w') as buff:
                buff.write(digraph)

            subprocess.run(f'dot -Tpng {tmp.name} -o {tmp_out.name}', shell=True, check=True)
        except Exception as e:
            logger.warning(e)
            return digraph
        return tmp_out

    @staticmethod
    def to_svg_string(root: Node | Graph, not_visible_graph: Graph | None = None) -> str:
        """
        Return a String containing an SVG image of translated root node.
        If Graphviz is not installed returns a String containing root Node translated into .dot graphic language
        :param not_visible_graph: Graph containing not visible triples
        :param root: translated root node or Graph containing triples
        :return: str containing an SVG image
        """
        output = []
        if isinstance(root, Node):
            digraph = DigraphWriter.node_to_digraph(root)
        elif isinstance(root, Graph) and isinstance(not_visible_graph, Graph):
            digraph = DigraphWriter.graph_to_digraph(root, not_visible_graph)
        else:
            return ""
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
            with open(tmp.name, 'w') as buff:
                buff.write(digraph)
            process = subprocess.Popen(f'dot -Tsvg {tmp.name}', shell=True, stdout=subprocess.PIPE, text=True)
            for line in process.stdout:
                output.append(line)
            process.wait()
            tmp.close()
            os.unlink(tmp.name)
        except Exception as e:
            logger.warning(e)
            return digraph
        if output:
            return ''.join(output)
        else:
            return digraph

    @staticmethod
    def check_visibility(root: Node) -> Node:
        for n in root.node_list:
            if not n.visibility:
                n.set_status(Glossary.NodeStatus.REMOVE)
        root.list = [n for n in root.node_list if n.status != Glossary.NodeStatus.REMOVE]
        for n in root.node_list:
            DigraphWriter.check_visibility(n)
        return root

    @staticmethod
    def graph_to_digraph(graph: Graph, not_visible_graph: Graph | None = None) -> str:
        if not_visible_graph is None:
            not_visible_graph = Graph
        digraph = Glossary.DIGRAPH_INI
        for s, p, o in graph:
            if (s, p, o) not in not_visible_graph:
                ss = graph.qname(s)
                pp = graph.qname(p)
                oo = graph.qname(o) if isinstance(o, URIRef) else o
                oo = oo.replace("\"", "'")
                shape = "box"
                digraph += f'"{ss}" [label="{ss}", shape={shape},'
                if ss.startswith(Glossary.FRED):
                    digraph += ' color="0.5 0.3 0.5"];\n'
                else:
                    digraph += ' color="1.0 0.3 0.7"];\n'
                digraph += f'"{oo}" [label="{oo}", shape={shape},'
                if oo.startswith(Glossary.FRED):
                    digraph += ' color="0.5 0.3 0.5"];\n'
                else:
                    digraph += ' color="1.0 0.3 0.7"];\n'
                digraph += f'"{ss}" -> "{oo}" [label="{pp}"];\n'
        return digraph + Glossary.DIGRAPH_END


class TafPostProcessor:
    current_directory = os.path.dirname(__file__)

    def __init__(self):
        self.dir_path = TafPostProcessor.current_directory
        self.framester_sparql = 'http://etna.istc.cnr.it/framester2/sparql'
        self.ewiser_wsd_url = 'https://arco.istc.cnr.it/ewiser/wsd'
        self.usea_preprocessing_url = 'https://arco.istc.cnr.it/usea/api/preprocessing'
        self.usea_wsd_url = 'https://arco.istc.cnr.it/usea/api/wsd'

        self.namespace_manager = NamespaceManager(Graph(), bind_namespaces="rdflib")

        self.prefixes = {
            "fred": Namespace("http://www.ontologydesignpatterns.org/ont/fred/domain.owl#"),
            "dul": Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#"),
            "d0": Namespace("http://www.ontologydesignpatterns.org/ont/d0.owl#"),
            "boxer": Namespace("http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#"),
            "boxing": Namespace("http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#"),
            "quant": Namespace("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#"),
            "vn.role": Namespace("http://www.ontologydesignpatterns.org/ont/vn/abox/role/vnrole.owl#"),
            "vn.data": Namespace("http://www.ontologydesignpatterns.org/ont/vn/data/"),
            "dbpedia": Namespace("http://dbpedia.org/resource/"),
            "schemaorg": Namespace("http://schema.org/"),
            "amr": Namespace("https://w3id.org/framester/amr/"),
            "amrb": Namespace("https://w3id.org/framester/amrb/"),
            "va": Namespace("http://verbatlas.org/"),
            "bn": Namespace("http://babelnet.org/rdf/"),
            "wn30schema": Namespace("https://w3id.org/framester/wn/wn30/schema/"),
            "wn30": Namespace("https://w3id.org/framester/wn/wn30/instances/"),
            "fschema": Namespace("https://w3id.org/framester/schema/"),
            "fsdata": Namespace("https://w3id.org/framester/data/framestercore/"),
            "pbdata": Namespace("https://w3id.org/framester/pb/data/"),
            "pblr": Namespace("https://w3id.org/framester/data/propbank-3.4.0/LocalRole/"),
            "pbrs": Namespace("https://w3id.org/framester/data/propbank-3.4.0/RoleSet/"),
            "pbschema": Namespace("https://w3id.org/framester/pb/schema/"),
            "fnframe": Namespace("https://w3id.org/framester/framenet/abox/frame/"),
            "wd": Namespace("http://www.wikidata.org/entity/"),
            "time": Namespace("https://www.w3.org/TR/xmlschema-2/#time"),
            "caus": Namespace("http://www.ontologydesignpatterns.org/ont/causal/causal.owl#"),
            "impact": Namespace("http://www.ontologydesignpatterns.org/ont/impact/impact.owl#"),
            "is": Namespace("http://www.ontologydesignpatterns.org/ont/is/is.owl#"),
            "mor": Namespace("http://www.ontologydesignpatterns.org/ont/values/moral.owl#"),
            "coerce": Namespace("http://www.ontologydesignpatterns.org/ont/coercion/coerce.owl#")
        }

        for prefix, namespace in self.prefixes.items():
            self.namespace_manager.bind(prefix, namespace)

        self.wn_pos = {
            "n": "noun",
            "v": "verb",
            "a": "adjective",
            "s": "adjectivesatellite",
            "r": "adverb"
        }

    def disambiguate(self, text: str, rdf_graph: Graph, namespace: str | None = Glossary.FRED_NS) -> Graph:
        if isinstance(rdf_graph, Graph):
            graph = rdf_graph
            graph.namespace_manager = self.namespace_manager
        else:
            return rdf_graph

        # SPARQL query to get the entities to disambiguate
        query = """
        SELECT DISTINCT ?entity
        WHERE {
            ?s ?p ?entity .
            FILTER REGEX(STR(?entity), STR(?prefix))
            FILTER NOT EXISTS {?entity a []}
            FILTER NOT EXISTS {?entity owl:sameAs []}
        }
        """
        result = graph.query(query, initBindings={"prefix": "^" + namespace + "[^_]+$"})
        if not result:
            logger.info("Returning initial graph, no entities to be disambiguated")
            return rdf_graph

        # Map each entity "name" (last part of the URI after the prefix) to its URI
        entities_to_uri = {}

        for entity in result:
            entity_name = entity["entity"][len(namespace):].lower()
            entities_to_uri[entity_name] = entity["entity"]

        # WSD over text
        wsd_result = self.wsd(text)

        disambiguated_entities = {}
        lemma_to_definition = {}
        for disambiguation in wsd_result:
            lemma = disambiguation["lemma"]
            if lemma in entities_to_uri:
                lemma_to_definition[lemma] = disambiguation["wnSynsetDefinition"]
                if lemma not in disambiguated_entities:
                    disambiguated_entities[lemma] = {disambiguation["wnSynsetName"]}
                else:
                    disambiguated_entities[lemma].add(disambiguation["wnSynsetName"])

        entity_to_disambiguation = {}
        wn_uris = set()
        lemma_to_wn30 = {}
        for lemma, disambiguations in disambiguated_entities.items():
            if len(disambiguations) == 1:
                synset_name = next(iter(disambiguations))
                synset_name_elements = synset_name.split(".")
                first_lemma = wordnet.synset(synset_name).lemma_names()[0]
                uri = f"https://w3id.org/framester/wn/wn30/instances/synset-{first_lemma}-{self.wn_pos[
                    synset_name_elements[1]]}-{re.sub('^0+', '', synset_name_elements[2])}"
                wn_uris.add(uri)
                lemma_to_wn30[lemma] = uri

        if not wn_uris:
            logger.info("Returning initial graph, no disambiguation found for entities")
            return rdf_graph

        wn_uris_values = ""
        for wn_uri in wn_uris:
            wn_uris_values += f"( <{wn_uri}> ) "
        wn_uris_values = wn_uris_values.strip()

        sparql_endpoint = SPARQLWrapper2(self.framester_sparql)

        wn_30_query = f"""
        SELECT DISTINCT ?wn
        WHERE {{
            VALUES (?wn) {{ {wn_uris_values} }}
            ?wn a [] .
        }}
        """

        sparql_endpoint.setQuery(wn_30_query)
        sparql_endpoint.setMethod(POST)

        wn_30_uris = set()
        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                if attempts > 1:
                    time.sleep(2)
                wn_30_uris = {result["wn"].value for result in sparql_endpoint.query().bindings}
                break
            except Exception as e:
                logger.warning(e)

        if not wn_30_uris:
            logger.info("Returning initial graph, no wn30 entities in framester or failed to call framester")
            return rdf_graph

        # wn_31_uris = wn_uris.difference(wn_30_uris)
        # wn_31_uris = {uri.replace("/wn30/", "/wn31/") for uri in wn_31_uris}

        for lemma, uri_wn30 in lemma_to_wn30.items():
            if uri_wn30 in wn_30_uris:
                graph.add((entities_to_uri[lemma], OWL.equivalentClass, URIRef(uri_wn30)))
                entity_to_disambiguation["<" + str(entities_to_uri[lemma]) + ">"] = "<" + uri_wn30 + ">"
            else:
                uri_wn31 = uri_wn30.replace("/wn30/", "/wn31/")
                graph.add((entities_to_uri[lemma], OWL.equivalentClass, URIRef(uri_wn31)))
                graph.add((URIRef(uri_wn31), URIRef("https://w3id.org/framester/wn/wn31/schema/gloss"),
                           Literal(lemma_to_definition[lemma], lang="en-us")))
                entity_to_disambiguation["<" + str(entities_to_uri[lemma]) + ">"] = "<" + uri_wn31 + ">"

                # graph.add((entities_to_uri[lemma], OWL.equivalentClass, URIRef(uri)))
                # entity_to_disambiguation["<"+str(entities_to_uri[lemma])+">"] = "<"+uri+">"

        if not entity_to_disambiguation:
            return rdf_graph

        query_values = ""
        for key, value in entity_to_disambiguation.items():
            query_values += f"( {key} {value} ) "

        query_values = query_values.strip()

        sparql_endpoint = SPARQLWrapper(self.framester_sparql)

        the_query = f"""
        CONSTRUCT {{
          ?entity rdfs:subClassOf ?lexname , ?d0dulType, ?dulQuality .
          ?wnClass <https://w3id.org/framester/wn/wn30/schema/gloss> ?gloss .
        }}
        WHERE {{
            SELECT DISTINCT * WHERE {{
            {{
            SELECT ?entity ?wnClass MAX(IF(?wnType IN (<https://w3id.org/framester/wn/wn30/schema/AdjectiveSynset>,
            <https://w3id.org/framester/wn/wn30/schema/AdjectiveSatelliteSynset>,
            <https://w3id.org/framester/wn/wn30/schema/AdverbSynset>),
            URI("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Quality"), ?undef)) as ?dulQuality
            WHERE {{
                VALUES (?entity ?wnClass) {{ {query_values} }}
                ?wnClass a ?wnType .
            }} group by ?entity ?wnClass
            }}
            OPTIONAL {{ ?wnClass <https://w3id.org/framester/wn/wn30/schema/lexname> ?lexname }}
            OPTIONAL {{ ?wnClass <http://www.ontologydesignpatterns.org/ont/own3/own2dul.owl#d0> ?d0 }}
            OPTIONAL {{ ?wnClass <https://w3id.org/framester/schema/ontoType> ?ontoType }}
            BIND(COALESCE(?ontoType, ?d0) as ?d0dulType)
            OPTIONAL {{ ?wnClass <https://w3id.org/framester/wn/wn30/schema/gloss> ?gloss }}
            }}
        }}
        """

        sparql_endpoint.setQuery(the_query)
        sparql_endpoint.setMethod(POST)

        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                if attempts > 1:
                    time.sleep(2)
                result_graph = sparql_endpoint.queryAndConvert()
                graph += result_graph

                return graph
            except Exception as e:
                logger.warning(e)

        logger.info("Returning initial graph: exception while querying SPARQL endpoint")
        return rdf_graph

    def wsd(self, text: str):
        response = requests.post(self.ewiser_wsd_url, json={"text": text})
        try:
            result = response.json()
        except Exception as e:
            logger.warning(e)
            result = []
        return result

    def disambiguate_usea(self, text: str, rdf_graph: Graph, namespace: str | None = Glossary.FRED_NS) -> Graph:
        if isinstance(rdf_graph, Graph):
            graph = rdf_graph
            graph.namespace_manager = self.namespace_manager
        else:
            return rdf_graph

        # SPARQL query to get the entities to disambiguate
        query = """
        SELECT DISTINCT ?entity
        WHERE {
            ?s ?p ?entity .
            FILTER REGEX(STR(?entity), STR(?prefix))
            FILTER NOT EXISTS {?entity a []}
            FILTER NOT EXISTS {?entity owl:sameAs []}
        }
        """
        result = graph.query(query, initBindings={"prefix": "^" + namespace + "[^_]+$"})
        if not result:
            logger.info("Returning initial graph, no entities to be disambiguated")
            return rdf_graph

        # Map each entity "name" (last part of the URI after the prefix) to its URI
        entities_to_uri = {}

        for entity in result:
            entity_name = entity["entity"][len(namespace):].lower()
            entities_to_uri[entity_name] = entity["entity"]

        # WSD over text
        wsd_result = self.wsd_usea(text)

        disambiguated_entities = {}
        lemma_to_definition = {}
        for disambiguation in wsd_result:
            nltk_synset_name = disambiguation["nltkSynset"]
            if nltk_synset_name != "O":
                lemma = disambiguation["lemma"]
                text = disambiguation["text"]
                nltk_synset = wordnet.synset(nltk_synset_name)
                definition = nltk_synset.definition()
                # consider both lemma and text
                if lemma in entities_to_uri:
                    lemma_to_definition[lemma] = definition
                    if lemma not in disambiguated_entities:
                        disambiguated_entities[lemma] = {nltk_synset_name}
                    else:
                        disambiguated_entities[lemma].add(nltk_synset_name)
                if text in entities_to_uri:
                    lemma_to_definition[text] = definition
                    if text not in disambiguated_entities:
                        disambiguated_entities[text] = {nltk_synset_name}
                    else:
                        disambiguated_entities[text].add(nltk_synset_name)

        entity_to_disambiguation = {}
        wn_uris = set()
        lemma_to_wn30 = {}
        for lemma, disambiguations in disambiguated_entities.items():
            if len(disambiguations) == 1:
                synset_name = next(iter(disambiguations))
                synset_name_elements = synset_name.split(".")
                first_lemma = wordnet.synset(synset_name).lemma_names()[0]
                uri = f"https://w3id.org/framester/wn/wn30/instances/synset-{first_lemma}-{self.wn_pos[
                    synset_name_elements[1]]}-{re.sub('^0+', '', synset_name_elements[2])}"
                wn_uris.add(uri)
                lemma_to_wn30[lemma] = uri

        if not wn_uris:
            logger.info("Returning initial graph, no disambiguation found for entities")
            return rdf_graph

        wn_uris_values = ""
        for wn_uri in wn_uris:
            wn_uris_values += f"( <{wn_uri}> ) "
        wn_uris_values = wn_uris_values.strip()

        sparql_endpoint = SPARQLWrapper2(self.framester_sparql)

        wn_30_query = f"""
        SELECT DISTINCT ?wn
        WHERE {{
            VALUES (?wn) {{ {wn_uris_values} }}
            ?wn a [] .
        }}
        """

        sparql_endpoint.setQuery(wn_30_query)
        sparql_endpoint.setMethod(POST)

        wn_30_uris = set()
        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                if attempts > 1:
                    time.sleep(2)
                wn_30_uris = {result["wn"].value for result in sparql_endpoint.query().bindings}
                break
            except Exception as e:
                logger.warning(e)

        if not wn_30_uris:
            logger.info("Returning initial graph, no wn30 entities in framester or failed to call framester")
            return rdf_graph

        # wn_31_uris = wn_uris.difference(wn_30_uris)
        # wn_31_uris = {uri.replace("/wn30/", "/wn31/") for uri in wn_31_uris}

        for lemma, uri_wn30 in lemma_to_wn30.items():
            if uri_wn30 in wn_30_uris:
                graph.add((entities_to_uri[lemma], OWL.equivalentClass, URIRef(uri_wn30)))
                entity_to_disambiguation["<" + str(entities_to_uri[lemma]) + ">"] = "<" + uri_wn30 + ">"
            else:
                uri_wn31 = uri_wn30.replace("/wn30/", "/wn31/")
                graph.add((entities_to_uri[lemma], OWL.equivalentClass, URIRef(uri_wn31)))
                graph.add((URIRef(uri_wn31), URIRef("https://w3id.org/framester/wn/wn31/schema/gloss"),
                           Literal(lemma_to_definition[lemma], lang="en-us")))
                entity_to_disambiguation["<" + str(entities_to_uri[lemma]) + ">"] = "<" + uri_wn31 + ">"

                # graph.add((entities_to_uri[lemma], OWL.equivalentClass, URIRef(uri)))
                # entity_to_disambiguation["<"+str(entities_to_uri[lemma])+">"] = "<"+uri+">"

        if not entity_to_disambiguation:
            return rdf_graph

        query_values = ""
        for key, value in entity_to_disambiguation.items():
            query_values += f"( {key} {value} ) "

        query_values = query_values.strip()

        sparql_endpoint = SPARQLWrapper(self.framester_sparql)

        the_query = f"""
        CONSTRUCT {{
          ?entity rdfs:subClassOf ?lexname , ?d0dulType, ?dulQuality .
          ?wnClass <https://w3id.org/framester/wn/wn30/schema/gloss> ?gloss .
        }}
        WHERE {{
            SELECT DISTINCT * WHERE {{
            {{
            SELECT ?entity ?wnClass MAX(IF(?wnType IN (<https://w3id.org/framester/wn/wn30/schema/AdjectiveSynset>,
            <https://w3id.org/framester/wn/wn30/schema/AdjectiveSatelliteSynset>,
            <https://w3id.org/framester/wn/wn30/schema/AdverbSynset>),
            URI("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Quality"), ?undef)) as ?dulQuality
            WHERE {{
                VALUES (?entity ?wnClass) {{ {query_values} }}
                ?wnClass a ?wnType .
            }} group by ?entity ?wnClass
            }}
            OPTIONAL {{ ?wnClass <https://w3id.org/framester/wn/wn30/schema/lexname> ?lexname }}
            OPTIONAL {{ ?wnClass <http://www.ontologydesignpatterns.org/ont/own3/own2dul.owl#d0> ?d0 }}
            OPTIONAL {{ ?wnClass <https://w3id.org/framester/schema/ontoType> ?ontoType }}
            BIND(COALESCE(?ontoType, ?d0) as ?d0dulType)
            OPTIONAL {{ ?wnClass <https://w3id.org/framester/wn/wn30/schema/gloss> ?gloss }}
            }}
        }}
        """

        sparql_endpoint.setQuery(the_query)
        sparql_endpoint.setMethod(POST)

        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                if attempts > 1:
                    time.sleep(2)
                result_graph = sparql_endpoint.queryAndConvert()
                graph += result_graph
                return graph
            except Exception as e:
                logger.warning(e)

        logger.info("Returning initial graph: exception while querying the SPARQL endpoint")
        return rdf_graph

    def wsd_usea(self, text: str):
        # preprocess
        text_input = {
            "type": "text",
            "content": text
        }
        response = requests.post(self.usea_preprocessing_url, json=text_input)
        result = response.json()
        # wsd
        text_input = {
            "sentence": result
        }
        response = requests.post(self.usea_wsd_url, json=text_input)
        result = response.json()

        return result["tokens"]

    def link_to_wikidata(self, rdf_graph: Graph) -> Graph:
        db_file_name = os.path.join(self.dir_path, "index_enwiki-latest.db")
        zip_db_file_name = os.path.join(self.dir_path, "index_enwiki-latest.zip")
        if not os.path.isfile(db_file_name) and not os.path.isfile(zip_db_file_name):
            if not os.path.isfile(zip_db_file_name):
                from tqdm import tqdm
                try:
                    url = "http://hrilabdemo.ddns.net/index_enwiki-latest.zip"
                    response = requests.get(url, stream=True)
                    logger.info("Downloading index_enwiki-latest db...")
                    with open(zip_db_file_name, "wb") as handle:
                        for data in tqdm(response.iter_content(chunk_size=1048576), total=832, desc="MBytes"):
                            handle.write(data)
                except Exception as e:
                    logger.warning(e)
                    return rdf_graph

        if not os.path.isfile(db_file_name) and os.path.isfile(zip_db_file_name):
            from zipfile import ZipFile
            with ZipFile(zip_db_file_name, 'r') as zObject:
                logger.info("Extracting db from zip-file...")
                zObject.extract("index_enwiki-latest.db", path=self.dir_path)
                zObject.close()

        if not os.path.isfile(db_file_name):
            return rdf_graph

        if os.path.isfile(zip_db_file_name):
            os.remove(zip_db_file_name)

        graph = rdf_graph
        graph.namespace_manager = self.namespace_manager

        # SPARQL query to get the entities aligned to dbpedia
        query = """
        SELECT ?entity ?dbpentity
        WHERE {
            ?entity owl:sameAs ?dbpentity .
            FILTER REGEX(STR(?dbpentity), "http://dbpedia.org/resource/")
        }
        """
        result = graph.query(query)
        if not result:
            logger.info("Returning initial graph, no entities to be linked to wikidata")
            return graph

        for binding in result:
            entity = binding["entity"]
            dbpentity = binding["dbpentity"]
            wiki_page_name = dbpentity[len("http://dbpedia.org/resource/"):]
            # print(f"{entity} --> {dbpentity} --> {wikiPageName}")
            # TODO implement verifying if db is present
            mapper = WikiMapper(db_file_name)
            wikidata_id = mapper.url_to_id("https://www.wikipedia.org/wiki/" + wiki_page_name)
            if wikidata_id:
                graph.add((URIRef(entity), OWL.sameAs, URIRef("http://www.wikidata.org/entity/" + wikidata_id)))

        return graph


class Amr2fred:
    def __init__(self):
        self.parser = Parser.get_parser()
        self.writer = RdfWriter()
        self.spring_uri = "https://arco.istc.cnr.it/spring/text-to-amr?blinkify=true&sentence="
        self.spring_uni_uri = "https://nlp.uniroma1.it/spring/api/text-to-amr?sentence="
        self.usea_uri = "https://arco.istc.cnr.it/usea/api/amr"
        self.taf = TafPostProcessor()

    def translate(self, amr: str | None = None,
                  mode: Glossary.RdflibMode = Glossary.RdflibMode.NT,
                  serialize: bool = True,
                  text: str | None = None,
                  alt_api: bool = False,
                  multilingual: bool = False,
                  graphic: str | None = None,
                  post_processing: bool = True,
                  alt_fred_ns: str | None = None) -> str | Graph | IO:
        if amr is None and text is None:
            return "Nothing to do!"

        if alt_fred_ns is not None:
            Glossary.FRED_NS = alt_fred_ns
            Glossary.NAMESPACE[0] = alt_fred_ns
        else:
            Glossary.FRED_NS = Glossary.DEFAULT_FRED_NS
            Glossary.NAMESPACE[0] = Glossary.DEFAULT_FRED_NS

        if amr is None and text is not None:
            amr = self.get_amr(text, alt_api, multilingual)
            if amr is None:
                return "Sorry, no amr!"

        root = self.parser.parse(amr)

        if post_processing:
            self.writer.to_rdf(root)
            graph = self.writer.graph
            if text is not None:
                if multilingual:
                    graph = self.taf.disambiguate_usea(text, graph)
                else:
                    graph = self.taf.disambiguate(text, graph)
            self.writer.graph = self.taf.link_to_wikidata(graph)
            if graphic is None:
                if serialize:
                    return self.writer.serialize(mode)
                else:
                    return self.writer.graph
            else:
                if graphic.lower() == "png":
                    file = DigraphWriter.to_png(self.writer.graph, self.writer.not_visible_graph)
                    return file
                else:
                    return DigraphWriter.to_svg_string(self.writer.graph, self.writer.not_visible_graph)
        else:
            if graphic is None:
                self.writer.to_rdf(root)
                if serialize:
                    return self.writer.serialize(mode)
                else:
                    return self.writer.graph
            else:
                if graphic.lower() == "png":
                    file = DigraphWriter.to_png(root)
                    return file
                else:
                    return DigraphWriter.to_svg_string(root)

    def get_amr(self, text, alt_api, multilingual):
        try:
            if multilingual:
                uri = self.usea_uri
                post_request = {
                    "sentence": {
                        "text": text
                    }
                }
                amr = json.loads(requests.post(uri, json=post_request).text).get("amr_graph")
            else:
                if alt_api:
                    uri = self.spring_uni_uri + urllib.parse.quote_plus(text)
                else:
                    uri = self.spring_uri + urllib.parse.quote_plus(text)
                amr = json.loads(requests.get(uri).text).get("penman")
            return amr
        except Exception as e:
            logger.warning(e)
