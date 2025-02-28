import os
import unittest
from unittest.mock import patch

from digraph_writer import DigraphWriter
from glossary import Glossary
from node import Node


class TestDigraphWriter(unittest.TestCase):
    def setUp(self):
        Node.endless = 0
        self.root = Node(Glossary.FRED + "entity1", Glossary.TOP)
        self.root.set_status(Glossary.NodeStatus.OK)
        self.child1 = Node(Glossary.FRED + "entity2", relation=Glossary.FRED + "hasRelation")
        self.child1.set_status(Glossary.NodeStatus.OK)
        self.child2 = Node(Glossary.FRED + "entity3", relation=Glossary.FRED + "hasOtherRelation")
        self.child2.set_status(Glossary.NodeStatus.OK)
        self.root.node_list.append(self.child1)
        self.root.node_list.append(self.child2)

    def test_node_to_digraph(self):
        """Test converting a Node structure to DOT format."""
        digraph_output = DigraphWriter.node_to_digraph(self.root)
        self.assertIn(Glossary.FRED + "entity1", digraph_output)
        self.assertIn(Glossary.FRED + "entity2", digraph_output)
        self.assertIn(Glossary.FRED + "hasRelation", digraph_output)
        self.assertIn(Glossary.FRED + "entity3", digraph_output)
        self.assertIn(Glossary.FRED + "hasOtherRelation", digraph_output)

    def test_to_digraph(self):
        """Test recursive conversion of nodes to DOT format."""
        digraph_fragment = DigraphWriter.to_digraph(self.root)
        self.assertIn('"fred:entity1" -> "fred:entity2" [label="fred:hasRelation"]', digraph_fragment)
        self.assertIn('"fred:entity1" -> "fred:entity3" [label="fred:hasOtherRelation"]', digraph_fragment)

    @patch("subprocess.Popen")
    def test_to_svg_string(self, mock_popen):
        """Test SVG output generation with a mock for subprocess.Popen."""
        mock_popen.return_value.stdout = ["<svg>Mock SVG</svg>"]
        mock_popen.return_value.wait.return_value = 0

        svg_output = DigraphWriter.to_svg_string(self.root)
        self.assertIn("<svg>Mock SVG</svg>", svg_output)

    @patch("subprocess.run")
    def test_to_png(self, mock_run):
        """Test PNG file generation (mocking subprocess)."""
        mock_run.return_value.returncode = 0  # Simulate successful execution

        temp_file = DigraphWriter.to_png(self.root)
        if isinstance(temp_file, str):
            self.assertIn("digraph", temp_file)  # Falls back to DOT if Graphviz fails
        else:
            self.assertTrue(os.path.exists(temp_file.name))
            # os.unlink(temp_file.name)  # Clean up


if __name__ == "__main__":
    unittest.main()
