import json
import logging
import urllib.parse
from typing import IO

import requests
from rdflib import Graph

from .digraph_writer import DigraphWriter
from .glossary import Glossary
from .parser import Parser
from .rdf_writer import RdfWriter
from .taf_post_processor import TafPostProcessor

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Amr2fred:
    """
        A class for transforming AMR (Abstract Meaning Representation) into RDF (Resource Description Framework)
        representations compliant with OWL ontologies.

        :param txt2amr_uri: Custom URI for the text-to-AMR service.
        :param m_txt2amr_uri: Custom URI for the multilingual text-to-AMR service.
    """
    def __init__(self, txt2amr_uri: str = None, m_txt2amr_uri: str = None):
        self.parser = Parser.get_parser()
        self.writer = RdfWriter()
        self.spring_uri = "https://arco.istc.cnr.it/spring/text-to-amr?blinkify=true&sentence="

        self.spring_uni_uri = ("https://nlp.uniroma1.it/spring/api/text-to-amr?sentence="
                               if txt2amr_uri is None else txt2amr_uri)
        self.usea_uri = ("https://arco.istc.cnr.it/usea/api/amr" if m_txt2amr_uri is None else m_txt2amr_uri)
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
        """
            Transforms an AMR representation or input text into an RDF graph or serialized format.

            :param amr: The AMR graph representation as a string.
            :param mode: The serialization format for RDF output (e.g., NT, TTL, RDF/XML).
            :param serialize: Whether to return the serialized RDF graph.
            :param text: The input text to be converted into AMR if `amr` is not provided.
            :param alt_api: Whether to use an alternative text-to-AMR API.
            :param multilingual: Whether to use the multilingual text-to-AMR service.
            :param graphic: If specified, returns a graphical representation ('png' or 'svg').
            :param post_processing: Whether to apply post-processing to enhance the RDF graph.
            :param alt_fred_ns: Alternative namespace for FRED RDF generation.
            :return: Serialized RDF graph, RDFLib Graph object, or graphical representation.
        """
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

    def get_amr(self, text: str, alt_api: bool, multilingual: bool) -> str | None:
        """
            Retrieves the AMR representation of the given text using the appropriate API.
            :param text: Input text to convert into AMR.
            :param alt_api: Whether to use the predefined alternative API or a custom one provided during class instantiation.
            :param multilingual: Whether to use the multilingual text-to-AMR service.
            :return: The AMR representation as a string.
        """
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
            logger.warning(str(e))
            return None
