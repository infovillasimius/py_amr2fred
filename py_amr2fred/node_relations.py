"""
NodeRelations: Parent-child relationships management

This module handles all relationship aspects of nodes including
parent-child relationships, node hierarchies, and graph structure management.
"""

from typing import List, Optional, Set, Iterator
from .node_core import NodeCore
from .exception_handler import recursion_guard


class NodeRelations:
    """
    Manages parent-child relationships and hierarchical structures.
    
    This class handles all aspects of node relationships including:
    - Parent-child connections
    - Hierarchy traversal
    - Relationship validation
    - Circular reference detection
    """
    
    def __init__(self, node_core: NodeCore):
        """
        Initialize relationship manager for a node.
        
        Args:
            node_core: The core node data this manages relationships for
        """
        self.core = node_core
        self.node_list: List['Node'] = []  # Child nodes
        self.parent: Optional['Node'] = None  # Primary parent
        self.parent_list: List['Node'] = []  # All parents (for non-tree structures)
        
    def add_child(self, child: 'Node') -> None:
        """
        Add a child node.
        
        Args:
            child: Node to add as child
        """
        if child not in self.node_list:
            self.node_list.append(child)
            # Set this as parent of the child
            if hasattr(child, 'relations'):
                child.relations.set_parent(self._get_node())
    
    def remove_child(self, child: 'Node') -> bool:
        """
        Remove a child node.
        
        Args:
            child: Node to remove from children
            
        Returns:
            True if child was removed, False if not found
        """
        if child in self.node_list:
            self.node_list.remove(child)
            # Remove parent reference from child
            if hasattr(child, 'relations'):
                child.relations.remove_parent(self._get_node())
            return True
        return False
    
    def get_children(self) -> List['Node']:
        """Get list of child nodes."""
        return self.node_list.copy()
    
    def get_child_count(self) -> int:
        """Get number of child nodes."""
        return len(self.node_list)
    
    def has_children(self) -> bool:
        """Check if node has any children."""
        return len(self.node_list) > 0
    
    def get_children_by_relation(self, relation: str) -> List['Node']:
        """
        Get child nodes with a specific relation.
        
        Args:
            relation: The relation to filter by
            
        Returns:
            List of child nodes with matching relation
        """
        return [child for child in self.node_list if hasattr(child, 'relation') and child.relation == relation]
    
    def set_parent(self, parent: 'Node') -> None:
        """
        Set the primary parent node.
        
        Args:
            parent: Node to set as parent
        """
        old_parent = self.parent
        self.parent = parent
        
        # Add to parent list if not already there
        if parent and parent not in self.parent_list:
            self.parent_list.append(parent)
        
        # Remove old parent from parent list if it was the only reference
        if old_parent and old_parent != parent and old_parent in self.parent_list:
            # Check if old parent is still referenced elsewhere
            if old_parent not in [p for p in self.parent_list if p != old_parent]:
                self.parent_list.remove(old_parent)
    
    def add_parent(self, parent: 'Node') -> None:
        """
        Add a parent node (for multi-parent structures).
        
        Args:
            parent: Node to add as parent
        """
        if parent not in self.parent_list:
            self.parent_list.append(parent)
        
        # Set as primary parent if none exists
        if not self.parent:
            self.parent = parent
    
    def remove_parent(self, parent: 'Node') -> bool:
        """
        Remove a parent node.
        
        Args:
            parent: Node to remove from parents
            
        Returns:
            True if parent was removed, False if not found
        """
        removed = False
        
        if parent in self.parent_list:
            self.parent_list.remove(parent)
            removed = True
        
        # Update primary parent if it was removed
        if self.parent == parent:
            self.parent = self.parent_list[0] if self.parent_list else None
        
        return removed
    
    def get_parent(self) -> Optional['Node']:
        """Get the primary parent node."""
        return self.parent
    
    def get_all_parents(self) -> List['Node']:
        """Get all parent nodes."""
        return self.parent_list.copy()
    
    def has_parent(self) -> bool:
        """Check if node has a parent."""
        return self.parent is not None
    
    def is_root(self) -> bool:
        """Check if this node is a root (no parents)."""
        return not self.has_parent()
    
    def is_leaf(self) -> bool:
        """Check if this node is a leaf (no children)."""
        return not self.has_children()
    
    def get_depth(self) -> int:
        """
        Get the depth of this node from root.
        
        Returns:
            Depth level (0 for root nodes)
        """
        if self.is_root():
            return 0
        
        # Use breadth-first search to avoid infinite recursion
        visited: Set['Node'] = set()
        current_node = self.parent
        depth = 1
        
        while current_node and current_node not in visited:
            visited.add(current_node)
            if hasattr(current_node, 'relations') and current_node.relations.has_parent():
                current_node = current_node.relations.get_parent()
                depth += 1
            else:
                break
        
        return depth
    
    def get_siblings(self) -> List['Node']:
        """
        Get sibling nodes (nodes with same parent).
        
        Returns:
            List of sibling nodes
        """
        if not self.has_parent():
            return []
        
        siblings = []
        parent_node = self.get_parent()
        if hasattr(parent_node, 'relations'):
            for child in parent_node.relations.get_children():
                if child != self._get_node():
                    siblings.append(child)
        
        return siblings
    
    @recursion_guard(max_depth=1000)
    def get_ancestors(self) -> List['Node']:
        """
        Get all ancestor nodes up to the root.
        
        Returns:
            List of ancestor nodes from immediate parent to root
        """
        ancestors = []
        current_parent = self.get_parent()
        
        while current_parent:
            ancestors.append(current_parent)
            if hasattr(current_parent, 'relations'):
                current_parent = current_parent.relations.get_parent()
            else:
                break
        
        return ancestors
    
    @recursion_guard(max_depth=1000)  
    def get_descendants(self) -> List['Node']:
        """
        Get all descendant nodes.
        
        Returns:
            List of all descendant nodes
        """
        descendants = []
        
        def collect_descendants(node_list: List['Node']) -> None:
            for child in node_list:
                descendants.append(child)
                if hasattr(child, 'relations'):
                    collect_descendants(child.relations.get_children())
        
        collect_descendants(self.get_children())
        return descendants
    
    def find_root(self) -> 'Node':
        """
        Find and return the root node of the tree.
        
        Returns:
            The root node
        """
        current_node = self._get_node()
        visited: Set['Node'] = set()
        
        while current_node and current_node not in visited:
            visited.add(current_node)
            if hasattr(current_node, 'relations') and current_node.relations.has_parent():
                current_node = current_node.relations.get_parent()
            else:
                break
        
        return current_node
    
    def is_ancestor_of(self, other: 'Node') -> bool:
        """
        Check if this node is an ancestor of another node.
        
        Args:
            other: Node to check
            
        Returns:
            True if this node is an ancestor of other
        """
        if not hasattr(other, 'relations'):
            return False
        
        ancestors = other.relations.get_ancestors()
        return self._get_node() in ancestors
    
    def is_descendant_of(self, other: 'Node') -> bool:
        """
        Check if this node is a descendant of another node.
        
        Args:
            other: Node to check
            
        Returns:
            True if this node is a descendant of other
        """
        if not hasattr(other, 'relations'):
            return False
        
        return other.relations.is_ancestor_of(self._get_node())
    
    def has_circular_reference(self) -> bool:
        """
        Check for circular references in the hierarchy.
        
        Returns:
            True if circular reference is detected
        """
        try:
            # Try to get ancestors - if there's a circle, recursion guard will trigger
            self.get_ancestors()
            return False
        except RecursionError:
            return True
    
    def _get_node(self) -> 'Node':
        """Get the complete node this relationship manager belongs to."""
        # This will be set by the Node class when it creates the relationship manager
        if hasattr(self, '_node_ref'):
            return self._node_ref
        raise RuntimeError("Node reference not set")
    
    def _set_node_reference(self, node: 'Node') -> None:
        """Set the reference to the complete node (used by Node class)."""
        self._node_ref = node