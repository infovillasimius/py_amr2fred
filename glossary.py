import json
from enum import Enum

import rdflib


def read_adjectives():
    try:
        with open("adjectives.json", "r", encoding="utf-8") as f:
            adj = json.load(f)
            return adj
    except Exception as e:
        print(e)
        return []


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

    DULS = {DUL_AGENT, DUL_CONCEPT, DUL_INFORMATION_ENTITY, DUL_ORGANISM, DUL_ORGANIZATION, DUL_SUBSTANCE, D0_TOPIC,
            D0_LOCATION}
    DULS_CHECK = {"agent", "concept", "informationentity", "organism", "organization", "substance", "topic", "location"}

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
    VN_ROLE_EXPERIENCER = VN_ROLE + "Expreriencer"
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

    _SCHEMA_NS = "http://www.w3.org/2001/XMLSchema#string"

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
    AMR_INVERSE = ":+.+-of"
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

    # Stringhe usate per la gestione del file predmatrix.txt
    PIVOT = "Pivot"
    NULL = "Null"
    PB = "pb:"
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

    # Jena's writers output modes
    RDF_MODE = ["json-ld", "n3", "nquads", "nt", "hext", "pretty-xml", "trig", "trix", "turtle", "longturtle", "xml"]

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

    # Field names of predmatrix table
    class LineFields(Enum):
        ID_POS = 0
        ID_PRED = 1
        ID_ROLE = 2
        VN_CLASS = 3
        VN_CLASS_NUMBER = 4
        VN_SUBCLASS = 5
        VN_SUBCLASS_NUMBER = 6
        VN_LEMA = 7
        VN_ROLE = 8
        WN_SENSE = 9
        MCR_iliOffset = 10
        FN_FRAME = 11
        FN_LE = 12
        FN_FRAME_ELEMENT = 13
        PB_ROLESET = 14
        PB_ARG = 15
        MCR_BC = 16
        MCR_DOMAIN = 17
        MCR_SUMO = 18
        MCR_TO = 19
        MCR_LEXNAME = 20
        MCR_BLC = 21
        WN_SENSEFREC = 22
        WN_SYNSET_REL_NUM = 23
        ESO_CLASS = 24
        ESO_ROLE = 25

    # Field names of pb2vn table
    class Pb2vnFields(Enum):
        PB_Role_URI = 0
        PB_RoleSet = 1
        PB_Role = 2
        VerbNet_Role_URI_for_FRED = 3
        VN_Role = 4
        VN_Sense = 5
        VerbNet_VerbSense_URI_for_FRED = 6

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

    # rdflib's writers output modes
    class RdfWriteMode(Enum):
        JSON_LD = 0
        N3 = 1
        NQUADS = 2
        NT = 3
        HEXT = 4
        PRETTY_XML = 5
        TRIG = 6
        TRIX = 7
        TURTLE = 8
        LONGTURTLE = 9
        XML = 10

    DISJUNCT = "disjunct"
    CONJUNCT = "conjunct"
    SPECIAL_INSTANCES = [DISJUNCT, CONJUNCT]
    SPECIAL_INSTANCES_PREFIX = [BOXING, BOXING]

    AMR_VALUE_INTERVAL = "value-interval"

    AMR_INSTANCES = ["thing", "person", "family", "animal", "language", "nationality", "ethnic-group", "regional-group",
                     "religious-group", "political-movement",
                     "organization", "company", "government-organization", "military", "criminal-organization",
                     "political-party",
                     "market-sector", "school", "university", "research-institute", "team", "league", "location",
                     "city", "city-district",
                     "county", "state", "province", "territory", "country", "local-region", "country-region",
                     "world-region", "continent",
                     "ocean", "sea", "lake", "river", "gulf", "bay", "strait", "canal", "peninsula", "mountain",
                     "volcano", "valley", "canyon",
                     "island", "desert", "forest", "moon", "planet", "star", "constellation", "facility", "airport",
                     "station", "port", "tunnel",
                     "bridge", "road", "railway-line", "canal", "building", "theater", "museum", "palace", "hotel",
                     "worship-place", "market",
                     "sports-facility", "park", "zoo", "amusement-park", "event", "incident", "natural-disaster",
                     "earthquake", "war",
                     "conference", "game", "festival", "product", "vehicle", "ship", "aircraft", "aircraft-type",
                     "spaceship", "car-make",
                     "work-of-art", "picture", "music", "show", "broadcast-program", "publication", "book", "newspaper",
                     "magazine",
                     "journal", "natural-object", "award", "law", "court-decision", "treaty", "music-key",
                     "musical-note",
                     "food-dish", "writing-script", "variable", "program", "molecular-physical-entity",
                     "small-molecule",
                     "protein", "protein-family", "protein-segment", "amino-acid", "macro-molecular-complex", "enzyme",
                     "nucleic-acid", "pathway", "gene", "dna-sequence", "cell", "cell-line", "species", "taxon",
                     "disease", "medical-condition"]
    AMR_ALWAYS_INSTANCES = [AMR_DATE_ENTITY, AMR_DATE_INTERVAL, "percentage-entity", "phone-number-entity",
                            "email-address-entity", "url-entity", "score-entity", "string-entity", AMR_VALUE_INTERVAL]

    OP_JOINER = "_"
    OP_NAME = "name"

    AMR_INTEGRATION = [AMR_ACCOMPANIER, AMR_BENEFICIARY, AMR_CAUSE, AMR_CONCESSION, AMR_DEGREE, AMR_DESTINATION,
                       AMR_DIRECTION, AMR_DURATION, AMR_EXAMPLE, AMR_EXTENT, AMR_FREQUENCY, AMR_INSTRUMENT,
                       AMR_LOCATION,
                       AMR_MANNER, AMR_MEDIUM, AMR_MOD, AMR_PART, AMR_PATH, AMR_POLARITY, AMR_PURPOSE, AMR_RANGE,
                       AMR_SOURCE, AMR_SUB_EVENT_OF, AMR_SUBSET, AMR_SUBSET_OF, AMR_TIME, AMR_TOPIC, AMR_AGE]

    FS_SCHEMA_SEMANTIC_ROLE = FS_SCHEMA + "SemanticRole"

    AGE_01 = "age-01"
    NEW_VAR = "newVar"
    SCALE = "_scale"
