import unittest

from glossary import Glossary
from node import Node


class TestNode(unittest.TestCase):

    def setUp(self):
        """Create sample nodes for testing."""
        self.node1 = Node(var="n1", relation="subj")
        self.node2 = Node(var="n2", relation="obj")
        self.node3 = Node(var="n3", relation=Glossary.INSTANCE)

    def test_initialization(self):
        """Test Node initialization."""
        self.assertEqual(self.node1.var, "n1")
        self.assertEqual(self.node1.relation, "subj")
        self.assertEqual(self.node1.status, Glossary.NodeStatus.AMR)
        self.assertTrue(self.node1.visibility)

    def test_string_representation(self):
        """Test __str__ method."""
        self.assertIsInstance(str(self.node1), str)

    def test_equality(self):
        """Test __eq__ method."""
        node1_copy = Node(var="n1", relation="subj")
        self.assertNotEqual(self.node1, node1_copy)  # Different instances should not be equal

    def test_add_child(self):
        """Test adding a child node."""
        self.node1.add(self.node2)
        self.assertIn(self.node2, self.node1.get_children("obj"))

    def test_get_instance(self):
        """Test retrieving an INSTANCE child."""
        self.node1.add(self.node3)
        instance_node = self.node1.get_instance()
        self.assertEqual(instance_node, self.node3)

    def test_get_child(self):
        """Test retrieving a specific child node."""
        self.node1.add(self.node2)
        child = self.node1.get_child("obj")
        self.assertEqual(child, self.node2)

    def test_make_equals(self):
        """Test setting the unique ID of a Node."""
        self.node1.make_equals(node=self.node2)
        self.assertEqual(self.node1.get_node_id(), self.node2.get_node_id())

    def test_copy_node(self):
        """Test creating a copy of a Node."""
        node_copy = self.node1.get_copy()
        self.assertNotEqual(id(self.node1), id(node_copy))  # Ensure different instances
        self.assertEqual(self.node1.var, node_copy.var)

    def test_set_status(self):
        """Test changing the status of a Node."""
        self.node1.set_status(Glossary.NodeStatus.OK)
        self.assertEqual(self.node1.status, Glossary.NodeStatus.OK)


if __name__ == "__main__":
    unittest.main()
