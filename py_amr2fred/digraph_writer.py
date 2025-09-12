import logging
import os
import subprocess
import tempfile
from typing import IO

from rdflib import Graph, URIRef

from .glossary import Glossary, get_glossary_instance
from .node import Node

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DigraphWriter:
    """
    A utility class for converting nodes and RDF graphs into Graphviz DOT format and generating graphical representations.

    This class provides methods to translate hierarchical structures of `Node` objects into the DOT language,
    allowing for visualization as PNG or SVG images. Additionally, it supports RDF graphs by generating DOT
    representations and linking nodes accordingly.
    """

    @staticmethod
    def node_to_digraph(root: Node):
        """
        Convert a root `Node` into DOT graph format.

        This method translates a given hierarchical node structure into the Graphviz DOT language.

        :param root: The root node to be converted.
        :type root: Node
        :return: A string representing the graph in DOT format.
        :rtype: str
        """
        # new_root = check_visibility(root)  # Uncomment if check_visibility is needed
        new_root = root

        glossary = get_glossary_instance()
        digraph = glossary.DIGRAPH_INI
        digraph += DigraphWriter.to_digraph(new_root)
        return digraph + glossary.DIGRAPH_END

    @staticmethod
    def to_digraph(root: Node) -> str:
        """
        Recursively generate a DOT representation of a `Node` and its connected sub-nodes.

        Nodes are styled based on their properties, such as `malformed` status and specific prefixes.

        :param root: The root node of the graph.
        :type root: Node
        :return: A string in DOT format representing the hierarchical structure.
        :rtype: str
        """
        glossary = get_glossary_instance()
        shape = "box"
        if root.malformed:
            shape = "ellipse"
        digraph = f'"{root.var}" [label="{root.var}", shape={shape},'
        if root.var.startswith(glossary.FRED):
            digraph += ' color="0.5 0.3 0.5"];\n'
        else:
            digraph += ' color="1.0 0.3 0.7"];\n'
        if root.node_list and root.get_tree_status() == 0:
            for a in root.node_list:
                if a.visibility:
                    shape = "ellipse" if a.malformed else "box"
                    digraph += f'"{a.var}" [label="{a.var}", shape={shape},'
                    if a.var.startswith(glossary.FRED):
                        digraph += ' color="0.5 0.3 0.5"];\n'
                    else:
                        digraph += ' color="1.0 0.3 0.7"];\n'
                    if a.relation.lower() != glossary.TOP.lower():
                        digraph += f'"{root.var}" -> "{a.var}" [label="{a.relation}"];\n'
                    digraph += DigraphWriter.to_digraph(a)
        return digraph

    @staticmethod
    def to_png(root: Node | Graph, not_visible_graph: Graph | None = None) -> IO | str:
        """
        Generate a PNG image of the graph representation.

        If Graphviz is installed, this method returns an image file of the translated root node or RDF graph.
        If Graphviz is not installed, it returns the DOT representation as a string.

        :param root: The root node or RDF graph to be visualized.
        :type root: Node | Graph
        :param not_visible_graph: An optional graph containing hidden triples.
        :type not_visible_graph: Graph, optional
        :return: A PNG image file if Graphviz is available, otherwise a DOT-format string.
        :rtype: IO | str
        """
        if isinstance(root, Node):
            digraph = DigraphWriter.node_to_digraph(root)
        elif isinstance(root, Graph) and isinstance(not_visible_graph, Graph):
            digraph = DigraphWriter.graph_to_digraph(root, not_visible_graph)
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
        Generate an SVG representation of the graph.

        If Graphviz is installed, it returns an SVG image as a string. Otherwise, it returns the DOT format
        representation.

        :param root: The root node or RDF graph to be visualized.
        :type root: Node | Graph
        :param not_visible_graph: An optional graph containing hidden triples.
        :type not_visible_graph: Graph, optional
        :return: A string containing the SVG representation of the graph.
        :rtype: str
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
        """
        Update the visibility status of nodes in the graph.

        This method iterates through the node hierarchy and removes nodes marked as invisible.

        :param root: The root node of the structure.
        :type root: Node
        :return: The updated root node with visibility-filtered sub-nodes.
        :rtype: Node
        """
        for n in root.node_list:
            if not n.visibility:
                n.set_status(Glossary.NodeStatus.REMOVE)
        root.list = [n for n in root.node_list if n.status != Glossary.NodeStatus.REMOVE]
        for n in root.node_list:
            DigraphWriter.check_visibility(n)
        return root

    @staticmethod
    def graph_to_digraph(graph: Graph, not_visible_graph: Graph | None = None) -> str:
        """
        Convert an RDF graph into DOT graph format.

        This method processes the RDF triples and translates them into DOT representation,
        applying styles based on specific prefixes.

        :param graph: The RDF graph to be converted.
        :type graph: Graph
        :param not_visible_graph: An optional graph containing hidden triples to be excluded.
        :type not_visible_graph: Graph, optional
        :return: A string in DOT format representing the RDF graph.
        :rtype: str
        """
        glossary = get_glossary_instance()
        if not_visible_graph is None:
            not_visible_graph = Graph
        digraph = glossary.DIGRAPH_INI
        for s, p, o in graph:
            if (s, p, o) not in not_visible_graph:
                ss = graph.qname(s)
                pp = graph.qname(p)
                oo = graph.qname(o) if isinstance(o, URIRef) else o
                oo = oo.replace("\"", "'")
                shape = "box"
                digraph += f'"{ss}" [label="{ss}", shape={shape},'
                if ss.startswith(glossary.FRED):
                    digraph += ' color="0.5 0.3 0.5"];\n'
                else:
                    digraph += ' color="1.0 0.3 0.7"];\n'
                digraph += f'"{oo}" [label="{oo}", shape={shape},'
                if oo.startswith(glossary.FRED):
                    digraph += ' color="0.5 0.3 0.5"];\n'
                else:
                    digraph += ' color="1.0 0.3 0.7"];\n'
                digraph += f'"{ss}" -> "{oo}" [label="{pp}"];\n'
        return digraph + glossary.DIGRAPH_END
