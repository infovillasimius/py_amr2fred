"""
Refactored Node Class

This module provides the new Node class that combines NodeCore, NodeRelations,
and NodeOperations for improved separation of concerns and maintainability.
"""

from typing import Optional, List, Dict, Any, Callable, Set
from enum import Enum
import copy
from .node_core import NodeCore
from .node_relations import NodeRelations
from .glossary import Glossary
from .exception_handler import recursion_guard


class CopyMode(Enum):
    """Modes for copying node structures."""
    SHALLOW = "shallow"
    DEEP = "deep" 
    STRUCTURE_ONLY = "structure_only"
    CHILDREN_ONLY = "children_only"


class Node:
    """
    Refactored Node class with separated concerns.
    
    This class combines three separate components:
    - NodeCore: Basic node data and identity
    - NodeRelations: Parent-child relationships 
    - NodeOperations: Tree operations and traversal
    
    This separation provides better testability, clearer responsibilities,
    and easier maintenance while maintaining backward compatibility.
    """
    
    def __init__(self, var: str, relation: str = "", 
                 status: Glossary.NodeStatus = Glossary.NodeStatus.AMR, 
                 visibility: bool = True):
        """
        Initialize a new Node instance.
        
        Args:
            var: The variable name (identifier) of the node
            relation: The relation that links this node to its parent
            status: The status of the node
            visibility: Whether the node is visible in graphical representation
        """
        # Initialize the two components
        self.core = NodeCore(var, relation, status, visibility)
        self.relations = NodeRelations(self.core)
        
        # Set node reference for relations component
        self.relations._set_node_reference(self)
        
        # Statistics tracking (from NodeOperations)
        self._level = 0  # Current traversal level
        self._endless_counter = 0  # Recursion counter
    
    # Backward compatibility properties - delegate to core
    @property
    def var(self) -> str:
        """Get the node variable."""
        return self.core.var
    
    @var.setter
    def var(self, value: str) -> None:
        """Set the node variable."""
        self.core.set_var(value)
    
    @property
    def relation(self) -> str:
        """Get the node relation."""
        return self.core.relation
    
    @relation.setter
    def relation(self, value: str) -> None:
        """Set the node relation."""
        self.core.set_relation(value)
    
    @property
    def label(self) -> str:
        """Get the node label."""
        return self.core.label
    
    @label.setter
    def label(self, value: str) -> None:
        """Set the node label."""
        self.core.set_label(value)
    
    @property
    def verb(self) -> str:
        """Get the node verb."""
        return self.core.verb
    
    @verb.setter
    def verb(self, value: str) -> None:
        """Set the node verb."""
        self.core.set_verb(value)
    
    @property
    def status(self) -> Glossary.NodeStatus:
        """Get the node status."""
        return self.core.status
    
    @status.setter
    def status(self, value: Glossary.NodeStatus) -> None:
        """Set the node status."""
        self.core.set_status(value)
    
    @property
    def node_type(self) -> Glossary.NodeType:
        """Get the node type."""
        return self.core.node_type
    
    @node_type.setter
    def node_type(self, value: Glossary.NodeType) -> None:
        """Set the node type."""
        self.core.set_node_type(value)
    
    @property
    def visibility(self) -> bool:
        """Get the node visibility."""
        return self.core.visibility
    
    @visibility.setter
    def visibility(self, value: bool) -> None:
        """Set the node visibility."""
        self.core.set_visibility(value)
    
    @property
    def prefix(self) -> bool:
        """Get the node prefix flag."""
        return self.core.prefix
    
    @prefix.setter
    def prefix(self, value: bool) -> None:
        """Set the node prefix flag."""
        self.core.set_prefix(value)
    
    @property
    def malformed(self) -> bool:
        """Get the node malformed flag."""
        return self.core.malformed
    
    @malformed.setter
    def malformed(self, value: bool) -> None:
        """Set the node malformed flag."""
        self.core.set_malformed(value)
    
    # Backward compatibility properties - delegate to relations
    @property
    def node_list(self) -> List['Node']:
        """Get the list of child nodes - returns reference to internal list for backward compatibility."""
        # Return reference to actual list, not copy, for backward compatibility
        return self.relations.node_list
    
    @node_list.setter
    def node_list(self, value: List['Node']) -> None:
        """Set the list of child nodes."""
        # Clear existing children and add new ones
        current_children = self.relations.get_children().copy()
        for child in current_children:
            self.relations.remove_child(child)
        
        for child in value:
            self.relations.add_child(child)
    
    @property
    def parent(self) -> Optional['Node']:
        """Get the parent node."""
        return self.relations.get_parent()
    
    @parent.setter
    def parent(self, value: Optional['Node']) -> None:
        """Set the parent node."""
        if value:
            self.relations.set_parent(value)
        else:
            # Remove all parents
            for parent in self.relations.get_all_parents():
                self.relations.remove_parent(parent)
    
    @property
    def parent_list(self) -> List['Node']:
        """Get all parent nodes."""
        return self.relations.get_all_parents()
    
    @parent_list.setter
    def parent_list(self, value: List['Node']) -> None:
        """Set all parent nodes."""
        # Clear existing parents and add new ones
        current_parents = self.relations.get_all_parents().copy()
        for parent in current_parents:
            self.relations.remove_parent(parent)
        
        for parent in value:
            self.relations.add_parent(parent)
    
    # Backward compatibility methods
    def get_var(self) -> str:
        """Get the node variable name."""
        return self.core.get_var()
    
    def set_var(self, var: str) -> None:
        """Set the node variable name."""
        self.core.set_var(var)
    
    def get_relation(self) -> str:
        """Get the node relation."""
        return self.core.get_relation()
    
    def set_relation(self, relation: str) -> None:
        """Set the node relation."""
        self.core.set_relation(relation)
    
    def get_status(self) -> Glossary.NodeStatus:
        """Get the node status."""
        return self.core.get_status()
    
    def set_status(self, status: Glossary.NodeStatus) -> None:
        """Set the node status."""
        self.core.set_status(status)
    
    def get_node_type(self) -> Glossary.NodeType:
        """Get the node type."""
        return self.core.get_node_type()
    
    def set_node_type(self, node_type: Glossary.NodeType) -> None:
        """Set the node type."""
        self.core.set_node_type(node_type)
    
    # Enhanced copy method replacing the complex get_copy()
    def get_copy(self, mode: CopyMode = CopyMode.DEEP) -> 'Node':
        """
        Get a copy of this node.
        
        Args:
            mode: Copy mode to use
            
        Returns:
            Copied node
        """
        return self.copy(mode)
    
    def copy(self, mode: CopyMode = CopyMode.DEEP) -> 'Node':
        """
        Create a copy of the node according to specified mode.
        
        This replaces the complex get_copy() method with clear copy strategies.
        
        Args:
            mode: Copy mode to use
            
        Returns:
            Copied node
        """
        if mode == CopyMode.SHALLOW:
            return self._shallow_copy()
        elif mode == CopyMode.DEEP:
            return self._deep_copy()
        elif mode == CopyMode.STRUCTURE_ONLY:
            return self._structure_copy()
        elif mode == CopyMode.CHILDREN_ONLY:
            return self._children_copy()
        else:
            raise ValueError(f"Unknown copy mode: {mode}")
    
    def _shallow_copy(self) -> 'Node':
        """Create a shallow copy (core data only, no children)."""
        new_node = Node(
            var=self.core.var,
            relation=self.core.relation,
            status=self.core.status,
            visibility=self.core.visibility
        )
        
        # Copy core attributes
        new_node.label = self.core.label
        new_node.verb = self.core.verb
        new_node.prefix = self.core.prefix
        new_node.node_type = self.core.node_type
        new_node.malformed = self.core.malformed
        
        return new_node
    
    @recursion_guard(max_depth=800)
    def _deep_copy(self) -> 'Node':
        """Create a deep copy (including all children recursively)."""
        # Create shallow copy first
        new_node = self._shallow_copy()
        
        # Recursively copy children
        for child in self.relations.get_children():
            child_copy = child._deep_copy()
            new_node.relations.add_child(child_copy)
        
        return new_node
    
    def _structure_copy(self) -> 'Node':
        """Create a copy of the structure without data."""
        new_node = Node(
            var=f"copy_{self.core.var}"[:50],  # Limit length to avoid issues
            relation=self.core.relation,
            status=self.core.status,
            visibility=self.core.visibility
        )
        
        # Copy structure for children
        for child in self.relations.get_children():
            child_copy = child._structure_copy()
            new_node.relations.add_child(child_copy)
        
        return new_node
    
    def _children_copy(self) -> 'Node':
        """Create a copy with only immediate children (no grandchildren)."""
        new_node = self._shallow_copy()
        
        # Copy immediate children only (shallow copy of each)
        for child in self.relations.get_children():
            child_copy = child._shallow_copy()
            new_node.relations.add_child(child_copy)
        
        return new_node
    
    # Tree traversal and search methods
    @recursion_guard(max_depth=1000)
    def depth_first_search(self, predicate: Callable[['Node'], bool]) -> Optional['Node']:
        """
        Perform depth-first search to find a node matching the predicate.
        
        Args:
            predicate: Function that returns True for the target node
            
        Returns:
            First node matching predicate, or None if not found
        """
        # Check current node
        if predicate(self):
            return self
        
        # Search children
        for child in self.relations.get_children():
            result = child.depth_first_search(predicate)
            if result:
                return result
        
        return None
    
    def breadth_first_search(self, predicate: Callable[['Node'], bool]) -> Optional['Node']:
        """
        Perform breadth-first search to find a node matching the predicate.
        
        Args:
            predicate: Function that returns True for the target node
            
        Returns:
            First node matching predicate, or None if not found
        """
        from collections import deque
        
        queue = deque([self])
        visited = set()
        
        while queue:
            current = queue.popleft()
            
            if current in visited:
                continue
            visited.add(current)
            
            if predicate(current):
                return current
            
            # Add children to queue
            for child in current.relations.get_children():
                if child not in visited:
                    queue.append(child)
        
        return None
    
    def find_by_var(self, var: str) -> Optional['Node']:
        """
        Find a node by its variable name.
        
        Args:
            var: Variable name to search for
            
        Returns:
            Node with matching variable, or None if not found
        """
        return self.depth_first_search(lambda node: node.core.var == var)
    
    def find_by_relation(self, relation: str) -> List['Node']:
        """
        Find all nodes with a specific relation.
        
        Args:
            relation: Relation to search for
            
        Returns:
            List of nodes with matching relation
        """
        results = []
        
        def collect_matches(node: 'Node') -> bool:
            if node.core.relation == relation:
                results.append(node)
            return False  # Continue searching
        
        self.depth_first_search(collect_matches)
        return results
    
    def find_by_status(self, status: Glossary.NodeStatus) -> List['Node']:
        """
        Find all nodes with a specific status.
        
        Args:
            status: Status to search for
            
        Returns:
            List of nodes with matching status
        """
        results = []
        
        def collect_matches(node: 'Node') -> bool:
            if node.core.status == status:
                results.append(node)
            return False  # Continue searching
        
        self.depth_first_search(collect_matches)
        return results
    
    # Utility methods
    def is_root(self) -> bool:
        """Check if this is a root node."""
        return self.relations.is_root()
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.relations.is_leaf()
    
    def get_depth(self) -> int:
        """Get the depth of this node from root."""
        return self.relations.get_depth()
    
    @recursion_guard(max_depth=1000)
    def traverse_with_level(self, visitor: Callable[['Node', int], None]) -> None:
        """
        Traverse the tree and call visitor with node and its level.
        
        Args:
            visitor: Function to call for each node (node, level)
        """
        self._traverse_with_level_recursive(self, visitor, 0, set())
    
    def _traverse_with_level_recursive(self, node: 'Node', 
                                     visitor: Callable[['Node', int], None],
                                     level: int, visited: Set['Node']) -> None:
        """Recursive helper for level traversal."""
        if node in visited:
            return
        
        visited.add(node)
        visitor(node, level)
        
        for child in node.relations.get_children():
            self._traverse_with_level_recursive(child, visitor, level + 1, visited)
    
    def get_tree_size(self) -> int:
        """
        Get the total number of nodes in the subtree.
        
        Returns:
            Total node count including this node
        """
        size = 1  # Count this node
        
        for child in self.relations.get_children():
            size += child.get_tree_size()
        
        return size
    
    def get_max_depth(self) -> int:
        """
        Get the maximum depth of the subtree.
        
        Returns:
            Maximum depth from this node
        """
        if not self.relations.has_children():
            return 0
        
        max_child_depth = 0
        for child in self.relations.get_children():
            child_depth = child.get_max_depth()
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth + 1
    
    def collect_all_vars(self) -> List[str]:
        """
        Collect all variable names in the subtree.
        
        Returns:
            List of all variable names
        """
        vars_list = [self.core.var]
        
        for child in self.relations.get_children():
            vars_list.extend(child.collect_all_vars())
        
        return vars_list
    
    def prune_by_status(self, status_to_remove: Glossary.NodeStatus) -> int:
        """
        Remove all nodes with a specific status from the subtree.
        
        Args:
            status_to_remove: Status of nodes to remove
            
        Returns:
            Number of nodes removed
        """
        removed_count = 0
        children_to_remove = []
        
        for child in self.relations.get_children():
            if child.core.status == status_to_remove:
                children_to_remove.append(child)
            else:
                removed_count += child.prune_by_status(status_to_remove)
        
        # Remove children with target status
        for child in children_to_remove:
            self.relations.remove_child(child)
            removed_count += 1
        
        return removed_count
    
    def to_dict(self, include_children: bool = True) -> Dict[str, Any]:
        """
        Convert node to dictionary representation.
        
        Args:
            include_children: Whether to include children in the output
            
        Returns:
            Dictionary representation of the node
        """
        result = {
            'id': self.core.node_id,
            'var': self.core.var,
            'relation': self.core.relation,
            'label': self.core.label,
            'verb': self.core.verb,
            'status': self.core.status.name if hasattr(self.core.status, 'name') else str(self.core.status),
            'node_type': self.core.node_type.name if hasattr(self.core.node_type, 'name') else str(self.core.node_type),
            'visibility': self.core.visibility,
            'prefix': self.core.prefix,
            'malformed': self.core.malformed,
            'has_parent': self.relations.has_parent(),
            'child_count': self.relations.get_child_count()
        }
        
        if include_children and self.relations.has_children():
            result['children'] = []
            for child in self.relations.get_children():
                result['children'].append(child.to_dict(include_children=True))
        
        return result
    
    # Class-level statistics (backward compatibility)
    unique_id = property(lambda self: self.core.node_id)
    level = 0  # This was a class variable, keeping for compatibility
    endless = 0  # This was a class variable, keeping for compatibility  
    endless2 = 0  # This was a class variable, keeping for compatibility
    
    # String representation with recursion protection
    @recursion_guard(max_depth=1000)
    def __str__(self) -> str:
        """String representation of the node."""
        return self._build_string_representation(0, set())
    
    def _build_string_representation(self, level: int, visited: set) -> str:
        """Build string representation with level and visited tracking."""
        if self in visited:
            return f"\\n{'\\t' * level}[CIRCULAR_REFERENCE: {self.var}]"
        
        visited.add(self)
        
        indent = "\\n" + "\\t" * level
        
        if self.relation != self.core.config.patterns.get_constant('top'):
            result = f"{indent}{{{self.relation} -> {self.var} -> "
        else:
            result = f"{{{self.var} -> "
        
        if self.relations.has_children():
            for i, child in enumerate(self.relations.get_children()):
                if i > 0:
                    result += " , "
                result += child._build_string_representation(level + 1, visited.copy())
        
        result += "}"
        visited.discard(self)
        return result
    
    def __eq__(self, other) -> bool:
        """Check equality based on node ID."""
        if not isinstance(other, Node):
            return False
        return self.core.node_id == other.core.node_id
    
    def __hash__(self) -> int:
        """Hash based on node ID."""
        return hash(self.core.node_id)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Node(id={self.core.node_id}, var='{self.var}', relation='{self.relation}')"
    
    # Backward compatibility methods for old Node API
    def add(self, child_node: 'Node') -> 'Node':
        """Add child node for backward compatibility."""
        self.relations.add_child(child_node)
        return child_node
    
    def get_child(self, relation: str) -> Optional['Node']:
        """Get child by relation for backward compatibility."""
        children = self.relations.get_children_by_relation(relation)
        return children[0] if children else None
    
    def get_children(self, relation: str) -> List['Node']:
        """Get children by relation for backward compatibility."""
        return self.relations.get_children_by_relation(relation)
        
    def get_instance(self) -> Optional['Node']:
        """Get INSTANCE child for backward compatibility."""
        return self.get_child("instance")
        
    def make_equals(self, node: 'Node') -> None:
        """Set node ID equal to another node for backward compatibility."""
        self.core._NodeCore__node_id = node.core._NodeCore__node_id
        
    def get_node_id(self) -> str:
        """Get node ID for backward compatibility."""
        return str(self.core._NodeCore__node_id)
    
    def get_tree_status(self) -> int:
        """
        Calculate the cumulative status of the node tree.
        
        Returns:
            Cumulative status value of node and all children
        """
        # Add recursion protection (from original implementation)
        if hasattr(self, '_status_calculation_depth'):
            self._status_calculation_depth += 1
        else:
            self._status_calculation_depth = 0
            
        if self._status_calculation_depth > 100:  # Prevent infinite recursion
            self._status_calculation_depth = 0
            return 1000000
        
        status_sum = self.status.value
        for child in self.node_list:
            status_sum += child.get_tree_status()
        
        self._status_calculation_depth = 0
        return status_sum