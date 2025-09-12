import logging
import os
import re
import time

import nltk
import requests
from SPARQLWrapper import SPARQLWrapper, POST, SPARQLWrapper2
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import OWL, NamespaceManager, Namespace
from wikimapper import WikiMapper

from .glossary import get_glossary_instance

nltk.download('wordnet')
from nltk.corpus import wordnet

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TafPostProcessor:
    """
    A class for post-processing RDF graphs by performing entity disambiguation using Word Sense Disambiguation (WSD)
    and linking entities to external knowledge bases.
    """
    current_directory = os.path.dirname(__file__)

    def __init__(self):
        """
        Initializes the TafPostProcessor with SPARQL endpoints, namespace bindings, and WordNet POS mappings.
        """
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

    def disambiguate(self, text: str, rdf_graph: Graph, namespace: str | None = None) -> Graph:
        """
        Disambiguates entities in an RDF graph using Word Sense Disambiguation (WSD) and links them to WordNet synsets.

        :param text: The input text associated with the RDF graph.
        :type text: str
        :param rdf_graph: The RDF graph to be processed.
        :type rdf_graph: Graph
        :param namespace: The namespace prefix (optional) for entities to be disambiguated.
        :type namespace: str

        :rtype: Graph
        :return: The updated RDF graph with disambiguated entities linked to WordNet.
        """
        if isinstance(rdf_graph, Graph):
            graph = rdf_graph
            graph.namespace_manager = self.namespace_manager
        else:
            return rdf_graph

        # Use default FRED namespace if none provided
        if namespace is None:
            glossary = get_glossary_instance()
            namespace = glossary.FRED_NS

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
                uri = f"https://w3id.org/framester/wn/wn30/instances/synset-{first_lemma}-{self.wn_pos[synset_name_elements[1]]}-{re.sub('^0+', '', synset_name_elements[2])}"
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

    def disambiguate_usea(self, text: str, rdf_graph: Graph, namespace: str | None = None) -> Graph:
        """
        Disambiguates entities in a multilingual RDF graph using Word Sense Disambiguation (WSD)
        with the Usea algorithm and aligns them with WordNet synsets.

        This method processes an RDF graph by identifying entities requiring disambiguation,
        performing WSD on the input text, and linking the identified entities to appropriate
        WordNet synsets (either WN30 or WN31). If no disambiguation is found, the original
        graph is returned unchanged.

        :param text: The textual content from which entities are disambiguated.
        :type text: str
        :param rdf_graph: The RDF graph containing entities to be disambiguated.
        :type rdf_graph: Graph
        :param namespace: The namespace prefix (optional) for filtering entities. Defaults to FRED namespace.

        :rtype: Graph
        :return: The updated RDF graph with entities linked to WordNet synsets when possible.
        """
        if isinstance(rdf_graph, Graph):
            graph = rdf_graph
            graph.namespace_manager = self.namespace_manager
        else:
            return rdf_graph

        # Use default FRED namespace if none provided
        if namespace is None:
            glossary = get_glossary_instance()
            namespace = glossary.FRED_NS

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
                uri = f"https://w3id.org/framester/wn/wn30/instances/synset-{first_lemma}-{self.wn_pos[synset_name_elements[1]]}-{re.sub('^0+', '', synset_name_elements[2])}"
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
        """
        Performs Word Sense Disambiguation (WSD) using the Usea services.

        This method preprocesses the input text and applies WSD via external Usea services.
        It first sends the text to a preprocessing endpoint and then performs WSD on the
        processed output, returning disambiguated tokens.

        :param text: The input text to be disambiguated.
        :type text: str
        :return: A list of disambiguated tokens with their associated sense information.
        :rtype: list
        """

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
        """
        Links entities in the RDF graph to Wikidata using Wikipedia mappings.

        This method identifies entities in the RDF graph that are aligned with DBpedia and
        attempts to link them to their corresponding Wikidata entities. It ensures that the
        required database for mapping is available, downloading and extracting it if necessary.

        :param rdf_graph: The input RDF graph containing entities to be linked.
        :type rdf_graph: Graph
        :return: The RDF graph with additional owl:sameAs links to Wikidata entities.
        :rtype: Graph
        """
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
