import re

from .glossary import Glossary


class Node:
    """
    Represents a node in a directed graph structure, used for hierarchical and semantic representations.

    :param var: The variable name (identifier) of the node.
    :param relation: The relation that links this node to its parent (default is an empty string).
    :param status: The status of the node, defaulting to `Glossary.NodeStatus.AMR`.
    :param visibility: Whether the node is visible in the graphic representation of the graph (default is True).

    Each node encapsulates a unique identifier (`var`), a relation (`relation`) connecting it to its parent,
    a list of child nodes (`node_list`), and additional metadata such as visibility, type, and status.

    Nodes can form tree-like structures where each node may have multiple child nodes.
    The `status` attribute represents the current processing state of the node, while `node_type` helps
    classify the node within the graph.

    Attributes:
        - unique_id (int): A class-level counter for uniquely identifying nodes.
        - level (int): Represents the depth of the node in the graph hierarchy.
        - endless (int): A flag used to track circular references or recursive processing.
        - endless2 (int): Additional flag for handling cyclic structures.

    Instance Attributes:
        - var (str): The variable name (identifier) of the node.
        - relation (str): The relation linking this node to its parent.
        - label (str): A human-readable label for the node.
        - node_list (list[Node]): A list of child nodes connected to this node.
        - parent (Node | None): The parent node in the hierarchy (if any).
        - parent_list (list[Node]): A list of all parent nodes (for non-tree structures).
        - visibility (bool): Whether the node is visible in the graphical representation.
        - prefix (bool): Determines whether the node has a prefix in its identifier.
        - status (Glossary.NodeStatus): The current processing status of the node.
        - node_type (Glossary.NodeType): The type classification of the node.
        - __node_id (int): A unique identifier assigned to each node instance.
        - verb (str): The main verb or identifier associated with the node.
        - malformed (bool): Indicates if the node contains malformed or inconsistent data.

    """
    unique_id = 0
    level = 0
    endless = 0
    endless2 = 0

    def __init__(self, var: str, relation: str, status: Glossary.NodeStatus = Glossary.NodeStatus.AMR, visibility=True):
        """
            Initializes a Node instance.

            :param var: The variable name (identifier) of the node.
            :param relation: The relation that links this node to its parent (default is an empty string).
            :param status: The status of the node, defaulting to `Glossary.NodeStatus.AMR`.
            :param visibility: Whether the node is visible in the graphic representation of the graph (default is True).
        """
        self.relation: str = relation
        self.label: str = ""
        self.var: str = var
        self.node_list: list[Node] = []
        self.parent: Node | None = None
        self.parent_list: list[Node] = []
        self.visibility: bool = visibility
        self.prefix: bool = False
        self.status: Glossary.NodeStatus = status
        self.node_type: Glossary.NodeType = Glossary.NodeType.OTHER
        self.__node_id: int = Node.unique_id
        Node.unique_id += 1
        self.verb: str = var
        self.malformed: bool = False

    def __str__(self):
        if Node.endless > Glossary.ENDLESS:
            return Glossary.RECURSIVE_ERROR
        stringa = "\n" + "\t" * Node.level
        if self.relation != Glossary.TOP:
            stringa = stringa + "{" + self.relation + " -> " + self.var + " -> "
        else:
            stringa = "{" + self.var + " -> "

        if len(self.node_list) > 0:
            Node.level += 1
            stringa = stringa + "[" + ", ".join([str(n) for n in self.node_list]) + ']}'
            Node.level -= 1
        else:
            stringa = stringa + "[" + ", ".join([str(n) for n in self.node_list]) + ']}'

        if self.status != Glossary.NodeStatus.OK and self.relation != Glossary.TOP:
            stringa = "\n" + "\t" * Node.level + "<error" + str(Node.level) + ">" + stringa + "</error" + str(
                Node.level) + ">"
        return stringa

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.__node_id == other.__node_id

    def to_string(self) -> str:
        if not self.visibility:
            return ""
        if Node.endless > Glossary.ENDLESS:
            return Glossary.RECURSIVE_ERROR
        stringa = "\n" + "\t" * Node.level
        if self.relation != Glossary.TOP:
            stringa = stringa + "{" + self.relation + " -> " + self.var + " -> "
        else:
            stringa = "{" + self.var + " -> "

        if len(self.node_list) > 0:
            Node.level += 1
            stringa = stringa + "[" + ", ".join([n.to_string() for n in self.node_list]) + ']}'
            Node.level -= 1
        else:
            stringa = stringa + "[" + ", ".join([n.to_string() for n in self.node_list]) + ']}'

        return stringa

    def get_instance(self):
        """
            Retrieves the node representing an instance from the node list.

            This method searches through the `node_list` for a node with a relation
            matching the `Glossary.INSTANCE` value. If found, it returns the node,
            otherwise, it returns `None`.

            :rtype: Node
            :return: The node representing an instance or `None` if no such node is found.
        """
        for node in self.node_list:
            if node.relation == Glossary.INSTANCE:
                return node
        return None

    def get_child(self, relation: str):
        """
            Retrieves a child node with a specific relation from the node list.

            This method searches the `node_list` for a node whose relation matches
            the given string `relation`. If found, it returns the node, otherwise,
            it returns `None`.

            :param relation: The relation to search for in the node list.

            :type relation: str
            :rtype: Node
            :return: The node with the matching relation or `None` if no such node is found.
        """
        if isinstance(relation, str):
            for node in self.node_list:
                if node.relation == relation:
                    return node
        return None

    def get_inverse(self):
        """
        Retrieves a node with an inverse relation from the node list.

        This method searches the `node_list` for a node whose relation matches
        the `Glossary.AMR_INVERSE` pattern, excluding certain relations. If such
        a node is found, it is returned; otherwise, `None` is returned.

        :rtype: Node
        :return: A node with an inverse relation or `None` if no such node is found.
        """
        for node in self.node_list:
            if (re.search(Glossary.AMR_INVERSE, node.relation) and
                    node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                    node.relation != Glossary.AMR_CONSIST_OF and
                    node.relation != Glossary.AMR_PART_OF and
                    node.relation != Glossary.AMR_SUB_EVENT_OF and
                    node.relation != Glossary.AMR_QUANT_OF and
                    node.relation != Glossary.AMR_SUBSET_OF):
                return node
        return None

    def get_inverses(self, nodes=None):
        """
        Retrieves all nodes with inverse relations from the node list.

        This method searches through the `node_list` for nodes whose relations
        match the `Glossary.AMR_INVERSE` pattern, excluding certain relations.
        The nodes are returned as a list. If the `nodes` parameter is provided,
        the method recursively adds inverse nodes to the given list.

        :param nodes: A list to accumulate inverse nodes (optional).
        :type nodes: list[Node], optional
        :rtype: list[Node]
        :return: A list of nodes with inverse relations.
        """
        if nodes is None:
            nodes: list[Node] = []
            for node in self.node_list:
                if (re.match(Glossary.AMR_INVERSE, node.relation) and
                        node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                        node.relation != Glossary.AMR_CONSIST_OF and
                        node.relation != Glossary.AMR_PART_OF and
                        node.relation != Glossary.AMR_SUB_EVENT_OF and
                        node.relation != Glossary.AMR_QUANT_OF and
                        node.relation != Glossary.AMR_SUBSET_OF and
                        node.status != Glossary.NodeStatus.REMOVE):
                    nodes.append(node)
        else:
            for node in self.node_list:
                if (re.match(Glossary.AMR_INVERSE, node.relation) and
                        node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                        node.relation != Glossary.AMR_CONSIST_OF and
                        node.relation != Glossary.AMR_PART_OF and
                        node.relation != Glossary.AMR_SUB_EVENT_OF and
                        node.relation != Glossary.AMR_QUANT_OF and
                        node.relation != Glossary.AMR_SUBSET_OF and
                        node.status != Glossary.NodeStatus.REMOVE):
                    nodes.append(node)
                nodes = node.get_inverses(nodes)
        return nodes

    def make_equals(self, node=None, node_id=None):
        """
        Sets the `__node_id` to be equal to that of the given node or node_id.

        This method sets the `__node_id` of the current object to either the `__node_id`
        of the provided `node` or the given `node_id`. Only one of the parameters can
        be specified.

        :param node: The node whose `__node_id` to copy.
        :type node: Node, optional
        :param node_id: The `__node_id` value to set.
        :type node_id: int, optional
        """
        if node is not None:
            self.__node_id = node.__node_id
        elif node_id is not None:
            self.__node_id = node_id

    def add(self, node):
        """
        Adds a node to the node list and sets its parent to the current node.

        This method appends the given `node` to the `node_list` and sets the current
        node as the parent of the given `node`.

        :param node: The node to be added.
        :type node: Node
        """
        self.node_list.append(node)
        node.parent = self

    def get_copy(self, node=None, relation=None, parser_nodes_copy=None):
        """
        Creates and returns a copy of the current node, or a copy of the provided node,
        based on the specified parameters.

        If no node is provided, a copy of the current node is created. If a specific node
        is provided, it will create a new node with the specified relation, or copy the
        provided node's properties and children. If `parser_nodes_copy` is provided,
        the new node is appended to this list.

        :param node: The node to copy, if specified. If not provided, the current node is copied.
        :param relation: The relation for the new node if specified. If not provided, the current relation is used.
        :param parser_nodes_copy: A list of nodes to which the new node is added if specified.
        :return: A new Node that is a copy of the current node or the provided node, based on the given parameters.
        :rtype: Node
        """

        # Preventing endless recursion by checking a threshold
        if Node.endless > Glossary.ENDLESS:
            return None

        # Case 1: If no node and relation are specified, create a full copy of the current node
        if node is None and relation is None and parser_nodes_copy is None:
            Node.endless += 1
            new_node = Node(self.var, self.relation, self.status)
            new_node.__node_id = self.__node_id
            for n in self.node_list:
                new_node.add(n.get_copy())
            return new_node

        # Case 2: If only relation is specified, create a new node with that relation
        if node is None and relation is not None and parser_nodes_copy is None:
            new_node = Node(self.var, relation, self.status)
            new_node.__node_id = self.__node_id
            return new_node

        # Case 3: If a specific node is provided, copy that node
        if node is not None and relation is not None and parser_nodes_copy is None:
            new_node = Node(node.var, relation, node.status)
            new_node.__node_id = node.__node_id
            for n in node.node_list:
                new_node.add(n)
            return new_node

        # Case 4: If parser_nodes_copy is provided, add the copy to that list
        if node is None and relation is None and parser_nodes_copy is not None:
            Node.endless += 1
            new_node = Node(self.var, self.relation, self.status)
            new_node.__node_id = self.__node_id
            parser_nodes_copy.append(new_node)
            for n in self.node_list:
                new_node.add(n)
            return new_node

    def get_snt(self):
        """
        Retrieves all nodes related to sentences from the node list.

        This method searches through the `node_list` for nodes whose relation
        matches the `Glossary.AMR_SENTENCE` pattern and returns them as a list.
        The method recursively collects sentence nodes from all child nodes.

        :rtype: list[Node]
        :return: A list of nodes related to sentences.
        """
        snt: list[Node] = []
        for node in self.node_list:
            if re.match(Glossary.AMR_SENTENCE, node.relation):
                snt.append(node)

        for node in self.node_list:
            snt += node.get_snt()
        return snt

    def get_args(self):
        """
        Retrieves all argument nodes from the node list.

        This method searches through the `node_list` for nodes whose relation
        matches the `Glossary.AMR_ARG` pattern and returns them as a list.

        :rtype: list[Node]
        :return: A list of argument nodes.
        """
        args_list: list[Node] = []
        for node in self.node_list:
            if re.match(Glossary.AMR_ARG, node.relation.lower()):
                args_list.append(node)
        return args_list

    def get_node_id(self) -> int:
        """
        Retrieves the node's ID.

        This method returns the unique identifier of the node.

        :rtype: int
        :return: The node's ID.
        """
        return self.__node_id

    def get_nodes_with_parent_list_not_empty(self) -> list:
        """
        Retrieves nodes that have a non-empty parent list.

        This method searches through the `node_list` and returns all nodes
        whose `parent_list` is not empty.

        :rtype: list[Node]
        :return: A list of nodes with a non-empty parent list.
        """
        snt = []
        for node in self.node_list:
            if len(node.parent_list) != 0:
                snt.append(node)
        return snt

    def get_children(self, relation):
        """
        Retrieves all child nodes with a specific relation.

        This method searches through the `node_list` and returns all nodes
        whose relation matches the given `relation`.

        :param relation: The relation to search for in the node list.
        :type relation: str
        :rtype: list[Node]
        :return: A list of child nodes with the given relation.
        """
        node_list: list[Node] = []
        for node in self.node_list:
            if node.relation == relation:
                node_list.append(node)
        return node_list

    def add_all(self, node_list):
        """
        Adds a list of nodes to the current node.

        This method appends all nodes from the given `node_list` to the `node_list`
        of the current node and sets the current node as their parent.

        :param node_list: A list of nodes to add.
        :type node_list: list[Node]
        """
        if isinstance(node_list, list):
            for node in node_list:
                node.parent = self
            self.node_list += node_list

    def set_status(self, status: Glossary.NodeStatus):
        """
        Sets the status of the node.

        This method sets the status of the current node to the specified `status`.

        :param status: The status to set for the node.
        :type status: Glossary.NodeStatus
        """
        self.status = status

    def get_ops(self):
        """
        Retrieves all 'operator' nodes from the node list.

        This method searches through the `node_list` for nodes whose relation
        matches the `Glossary.AMR_OP` pattern and returns them as a list.

        :rtype: list[Node]
        :return: A list of 'operator' nodes.
        """
        ops_list: list[Node] = []
        for node in self.node_list:
            if re.match(Glossary.AMR_OP, node.relation):
                ops_list.append(node)
        return ops_list

    def get_poss(self):
        """
        Retrieves the 'possession' node from the node list.

        This method searches through the `node_list` for a node whose relation
        matches the `Glossary.AMR_POSS` pattern. If found, the node is returned.

        :rtype: Node
        :return: The 'possession' node or `None` if not found.
        """
        for node in self.node_list:
            if re.match(Glossary.AMR_POSS, node.relation):
                return node

    def substitute(self, node):
        """
        Substitutes the current node with another node.

        This method copies the properties of the given `node` to the current node,
        including its `var`, `relation`, `__node_id`, and `node_list`. The parent
        and other attributes are also updated accordingly.

        :param node: The node to substitute.
        :type node: Node
        """
        if isinstance(node, Node):
            self.var = node.var
            self.relation = node.relation
            self.__node_id = node.__node_id
            self.node_list = []
            self.add_all(node.node_list)
            self.status = node.status
            self.node_type = node.node_type
            self.verb = node.verb

    def get_tree_status(self):
        """
        Retrieves the status of the entire node tree.

        This method calculates the cumulative status value of the node tree,
        starting from the current node and recursively including all child nodes.

        :rtype: int
        :return: The cumulative status value of the node tree.
        """
        if Node.endless > Glossary.ENDLESS:
            return 1000000

        somma = self.status.value  # Assuming `status` is an Enum and `ordinal()` is similar to `value` in Python Enum
        for n in self.node_list:
            somma += n.get_tree_status()

        return somma
