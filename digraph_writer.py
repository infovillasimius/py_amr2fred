import logging
import os
import subprocess
import tempfile
from typing import IO

from rdflib import Graph, URIRef

from glossary import Glossary
from node import Node

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
