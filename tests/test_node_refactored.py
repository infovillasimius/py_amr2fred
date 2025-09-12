"""Tests for the refactored Node components."""

import unittest
from py_amr2fred.node_refactored import Node, CopyMode
from py_amr2fred.config_manager import NodeStatus, NodeType
from py_amr2fred.glossary import Glossary


class TestNodeRefactored(unittest.TestCase):

    def setUp(self):
        """Set up test nodes."""
        self.root = Node("root", "top")
        self.child1 = Node("child1", ":arg0")
        self.child2 = Node("child2", ":arg1")
        self.grandchild = Node("grandchild", ":mod")

    def test_node_initialization(self):
        """Test basic node initialization."""
        node = Node("test", ":relation")
        self.assertEqual(node.var, "test")
        self.assertEqual(node.relation, ":relation")
        self.assertEqual(node.status, Glossary.NodeStatus.AMR)
        self.assertTrue(node.visibility)

    def test_core_properties(self):
        """Test core property access."""
        node = Node("test", ":relation")
        
        # Test getters
        self.assertEqual(node.get_var(), "test")
        self.assertEqual(node.get_relation(), ":relation")
        self.assertEqual(node.get_status(), Glossary.NodeStatus.AMR)
        
        # Test setters
        node.set_var("new_var")
        node.set_relation(":new_relation")
        node.set_status(Glossary.NodeStatus.OK)
        
        self.assertEqual(node.var, "new_var")
        self.assertEqual(node.relation, ":new_relation")
        self.assertEqual(node.status, Glossary.NodeStatus.OK)

    def test_relationship_management(self):
        """Test parent-child relationships."""
        # Add children
        self.root.relations.add_child(self.child1)
        self.root.relations.add_child(self.child2)
        
        # Test children access
        children = self.root.relations.get_children()
        self.assertEqual(len(children), 2)
        self.assertIn(self.child1, children)
        self.assertIn(self.child2, children)
        
        # Test parent access
        self.assertEqual(self.child1.relations.get_parent(), self.root)
        
        # Test backward compatibility
        self.assertEqual(len(self.root.node_list), 2)
        self.assertEqual(self.child1.parent, self.root)

    def test_tree_structure_queries(self):
        """Test tree structure queries."""
        # Build hierarchy
        self.root.relations.add_child(self.child1)
        self.child1.relations.add_child(self.grandchild)
        
        # Test structure queries
        self.assertTrue(self.root.is_root())
        self.assertFalse(self.child1.is_root())
        self.assertTrue(self.grandchild.is_leaf())
        self.assertFalse(self.child1.is_leaf())
        
        # Test depth
        self.assertEqual(self.root.get_depth(), 0)
        self.assertEqual(self.child1.get_depth(), 1)
        self.assertEqual(self.grandchild.get_depth(), 2)

    def test_node_copying(self):
        """Test different copy modes."""
        self.root.relations.add_child(self.child1)
        self.child1.relations.add_child(self.grandchild)
        
        # Test shallow copy
        shallow_copy = self.root.copy(CopyMode.SHALLOW)
        self.assertEqual(shallow_copy.var, self.root.var)
        self.assertEqual(len(shallow_copy.node_list), 0)  # No children
        
        # Test deep copy
        deep_copy = self.root.copy(CopyMode.DEEP)
        self.assertEqual(deep_copy.var, self.root.var)
        self.assertEqual(len(deep_copy.node_list), 1)  # Has children
        
        # Test backward compatibility
        legacy_copy = self.root.get_copy()
        self.assertEqual(legacy_copy.var, self.root.var)

    def test_search_operations(self):
        """Test search functionality."""
        self.root.relations.add_child(self.child1)
        self.root.relations.add_child(self.child2)
        self.child1.relations.add_child(self.grandchild)
        
        # Test find by variable
        found = self.root.find_by_var("child1")
        self.assertEqual(found, self.child1)
        
        # Test find by relation
        arg_nodes = self.root.find_by_relation(":arg0")
        self.assertIn(self.child1, arg_nodes)
        
        # Test find by status
        self.child2.set_status(NodeStatus.OK)
        ok_nodes = self.root.find_by_status(NodeStatus.OK)
        self.assertIn(self.child2, ok_nodes)

    def test_tree_statistics(self):
        """Test tree size and depth calculations."""
        self.root.relations.add_child(self.child1)
        self.root.relations.add_child(self.child2)
        self.child1.relations.add_child(self.grandchild)
        
        # Test tree size
        size = self.root.get_tree_size()
        self.assertEqual(size, 4)  # root + 2 children + 1 grandchild
        
        # Test max depth
        max_depth = self.root.get_max_depth()
        self.assertEqual(max_depth, 2)  # root -> child -> grandchild

    def test_node_equality(self):
        """Test node equality and hashing."""
        node1 = Node("test", ":relation")
        node2 = Node("test", ":relation")
        
        # Nodes with same content but different IDs should not be equal
        self.assertNotEqual(node1, node2)
        self.assertNotEqual(hash(node1), hash(node2))
        
        # Node should equal itself
        self.assertEqual(node1, node1)
        self.assertEqual(hash(node1), hash(node1))

    def test_dictionary_conversion(self):
        """Test conversion to dictionary representation."""
        self.root.relations.add_child(self.child1)
        
        node_dict = self.root.to_dict()
        
        self.assertEqual(node_dict['var'], 'root')
        self.assertEqual(node_dict['relation'], 'top')
        self.assertTrue(node_dict['has_parent'] == False)  # Root has no parent
        self.assertEqual(node_dict['child_count'], 1)
        self.assertIn('children', node_dict)

    def test_string_representation(self):
        """Test string representation."""
        self.root.relations.add_child(self.child1)
        
        str_repr = str(self.root)
        self.assertIn("root", str_repr)
        self.assertIn("child1", str_repr)
        
        # Test circular reference detection
        # Create circular reference
        self.child1.relations.add_child(self.root)  # This creates a cycle
        
        # Should not cause infinite recursion
        str_repr = str(self.root)
        self.assertIsInstance(str_repr, str)  # Should complete without error


if __name__ == '__main__':
    unittest.main()