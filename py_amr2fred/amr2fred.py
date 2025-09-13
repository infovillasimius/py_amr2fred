import json
import logging
import urllib.parse
from typing import IO, Optional

import requests
from rdflib import Graph

from .digraph_writer import DigraphWriter
from .glossary import Glossary, get_glossary_instance
from .parser import Parser
from .rdf_writer import RdfWriter
from .taf_post_processor import TafPostProcessor
from .interfaces.Itxt2amr import IText2AMR
from .txt2amr import Text2AMR

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

    def __init__(self,
            txt2amr_uri: Optional[str] = None,
            m_txt2amr_uri: Optional[str] = None,
            txt2amr: Optional[IText2AMR] = None
        ):
        self.parser = Parser.get_parser()
        self.writer = RdfWriter()
        self.spring_uri = "https://arco.istc.cnr.it/spring/text-to-amr?blinkify=true&sentence="
        self.glossary = get_glossary_instance()
        self.taf = TafPostProcessor()
        self.txt2amr = txt2amr if txt2amr else Text2AMR(
            txt2amr_uri=txt2amr_uri,
            m_txt2amr_uri=m_txt2amr_uri
        )

    def translate(self,
                  amr: str | None = None,
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
            :return: Serialized RDF graph, RDFLib Graph object, or graphical representation (DOT format).
        """
        if amr is None and text is None:
            return "Nothing to do!"

        if alt_fred_ns is not None:
            self.glossary.FRED_NS = alt_fred_ns
        else:
            # Reset to default namespace
            default_ns = self.glossary.DEFAULT_FRED_NS
            self.glossary.FRED_NS = default_ns

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

    def get_amr(self,
            text: str,
            alt_api: bool,
            multilingual: bool
        ) -> str | None:
        """
            Retrieves the AMR representation of the given text using the appropriate API.
            :param text: Input text to convert into AMR.
            :param alt_api: Whether to use the predefined alternative API or a custom one provided during class instantiation.
            :param multilingual: Whether to use the multilingual text-to-AMR service.
            :return: The AMR representation as a string.
        """
        return self.txt2amr.get_amr(
            text=text,
            alt_api=alt_api,
            multilingual=multilingual
        )
