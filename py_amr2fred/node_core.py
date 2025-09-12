"""
NodeCore: Basic node data and identity

This module contains the core data structures and basic functionality
for nodes, separated from relationship management and operations.
"""

from typing import Optional
from .config_manager import ConfigurationManager, NodeStatus, NodeType
from .exception_handler import recursion_guard


class NodeCore:
    """
    Core node data and identity management.
    
    This class handles the fundamental data and identity aspects of nodes,
    including unique ID generation, status management, and basic attributes.
    """
    
    _unique_id_counter = 0
    
    def __init__(self, var: str, relation: str, 
                 status: NodeStatus = NodeStatus.AMR, 
                 visibility: bool = True):
        """
        Initialize core node data.
        
        Args:
            var: The variable name (identifier) of the node
            relation: The relation that links this node to its parent
            status: The status of the node
            visibility: Whether the node is visible in graphical representation
        """
        # Core identity
        self.var: str = var
        self.relation: str = relation
        self.__node_id: int = self._get_next_id()
        
        # Basic attributes
        self.label: str = ""
        self.verb: str = var
        self.visibility: bool = visibility
        self.prefix: bool = False
        self.malformed: bool = False
        
        # Status and type
        self.status: NodeStatus = status
        self.node_type: NodeType = NodeType.OTHER
        
        # Configuration access
        self.config = ConfigurationManager.get_instance()
    
    @classmethod
    def _get_next_id(cls) -> int:
        """Get the next unique ID for a node."""
        cls._unique_id_counter += 1
        return cls._unique_id_counter
    
    @property
    def node_id(self) -> int:
        """Get the unique node ID."""
        return self.__node_id
    
    def get_var(self) -> str:
        """Get the node variable name."""
        return self.var
    
    def set_var(self, var: str) -> None:
        """Set the node variable name."""
        self.var = var
        # Update verb if it was the same as var
        if self.verb == self.var:
            self.verb = var
    
    def get_relation(self) -> str:
        """Get the node relation."""
        return self.relation
    
    def set_relation(self, relation: str) -> None:
        """Set the node relation."""
        self.relation = relation
    
    def get_label(self) -> str:
        """Get the node label."""
        return self.label
    
    def set_label(self, label: str) -> None:
        """Set the node label."""
        self.label = label
    
    def get_verb(self) -> str:
        """Get the node verb."""
        return self.verb
    
    def set_verb(self, verb: str) -> None:
        """Set the node verb."""
        self.verb = verb
    
    def get_status(self) -> NodeStatus:
        """Get the node status."""
        return self.status
    
    def set_status(self, status: NodeStatus) -> None:
        """Set the node status."""
        self.status = status
    
    def get_node_type(self) -> NodeType:
        """Get the node type."""
        return self.node_type
    
    def set_node_type(self, node_type: NodeType) -> None:
        """Set the node type."""
        self.node_type = node_type
    
    def is_visible(self) -> bool:
        """Check if the node is visible."""
        return self.visibility
    
    def set_visibility(self, visibility: bool) -> None:
        """Set the node visibility."""
        self.visibility = visibility
    
    def has_prefix(self) -> bool:
        """Check if the node has a prefix."""
        return self.prefix
    
    def set_prefix(self, prefix: bool) -> None:
        """Set the node prefix flag."""
        self.prefix = prefix
    
    def is_malformed(self) -> bool:
        """Check if the node is malformed."""
        return self.malformed
    
    def set_malformed(self, malformed: bool) -> None:
        """Set the node malformed flag."""
        self.malformed = malformed
    
    def is_top(self) -> bool:
        """Check if this is the top/root relation."""
        top_constant = self.config.patterns.get_constant('top')
        return self.relation == top_constant
    
    def is_instance_relation(self) -> bool:
        """Check if this is an instance relation."""
        instance_constant = self.config.patterns.get_constant('instance')
        return self.relation == instance_constant
    
    def __eq__(self, other) -> bool:
        """Check equality based on node ID."""
        if not isinstance(other, NodeCore):
            return False
        return self.node_id == other.node_id
    
    def __hash__(self) -> int:
        """Hash based on node ID."""
        return hash(self.node_id)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"NodeCore(id={self.node_id}, var='{self.var}', relation='{self.relation}')"