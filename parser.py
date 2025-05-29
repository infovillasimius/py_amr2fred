import re

from unidecode import unidecode

from .couple import Couple
from .glossary import *
from .node import Node
from .propbank import Propbank


class Parser:
    """
    A class for parsing Abstract Meaning Representation (AMR) strings and transforming them
    into nodes representing logical structure.

    This class provides methods to parse an AMR string, manipulate its nodes, and process
    multi-sentence, recursive, and logical error handling. It also integrates semantic
    information through specific transformations.

    Attributes:
        - nodes (list): A list of nodes generated during parsing.
        - nodes_copy (list): A copy of the node list.
        - couples (list): A list of couples (pairs of related nodes).
        - removed (list): A list of nodes removed during parsing.
        - to_add (list): A list of nodes to be added during parsing.
        - vars (list): A list of variables used during parsing.
        - root_copy (Node): A copy of the root node.
        - topic_flag (bool): A flag indicating whether the topic node should be added.
        - __parser (Parser): The singleton instance of the Parser class.

    """

    __parser = None

    def __init__(self):
        self.nodes = []
        self.nodes_copy = []
        self.couples = []
        self.removed = []
        self.to_add = []
        self.vars = []
        self.root_copy = None
        self.topic_flag = True
        Parser.__parser = self

    @staticmethod
    def get_parser():
        """
        Returns the singleton instance of the Parser class.

        If an instance of the Parser class does not exist, it will create and return one.

        :rtype: Parser
        """
        if Parser.__parser is None:
            Parser.__parser = Parser()
        return Parser.__parser

    def reinitialise(self):
        """
        Resets the internal structures before a new parsing run.
        """
        self.nodes = []
        self.nodes_copy = []
        self.couples = []
        self.removed = []
        self.to_add = []
        self.vars = []
        self.root_copy = None
        self.topic_flag = True

    def string2array(self, amr: str) -> list[str] | None:
        """
        Converts an AMR string into a list of words, normalizing and processing special characters
        as necessary.

        This method processes the input AMR string and splits it into a list of words. It handles
        normalizations such as converting words to lowercase and replacing special characters like
        spaces, quotes, and underscores. Words that are quoted are processed to preserve their
        meaning in the AMR structure.

        If an error occurs during processing (such as a malformed string), the method logs a warning
        and returns `None`.

        :param amr: The AMR string to convert.
        :type amr: str
        :return: A list of words extracted from the AMR string, or `None` if an error occurs.
        :rtype: list[str] | None
        """
        word_list = []
        amr = self.normalize(amr)

        try:
            while len(amr) > 1:
                inizio = amr.index(" ") + 1
                fine = amr.index(" ", inizio)
                word = amr[inizio:fine]

                if not word.startswith(Glossary.QUOTE):
                    word_list.append(word.lower())
                else:
                    fine = amr.index(Glossary.QUOTE, inizio + 1)
                    word = amr[inizio: fine]
                    word = word.strip()
                    while "  " in word:
                        word = word.replace("  ", " ")

                    word = word.replace(" ", "_")
                    word = word.replace("__", "_")
                    word = word.replace("(_", "(")
                    word = word.replace("_)", ")")
                    word = word.replace("_/_", "/")
                    while Glossary.QUOTE in word:
                        word = word.replace(Glossary.QUOTE, "")

                    word_list.append(Glossary.LITERAL + word.replace(Glossary.QUOTE, ""))

                amr = amr[fine:]

        except Exception as e:
            logger.warning(e)
            return None

        return word_list

    @staticmethod
    def normalize(amr: str) -> str:
        """
        Normalizes an AMR string by replacing newline characters and adjusting spacing.

        This method processes the input AMR string by performing several normalization steps:

        - Converts carriage returns and newline characters to spaces.
        - Strips leading and trailing whitespace.
        - Adds spaces around parentheses and slashes for consistent formatting.
        - Replaces tabs with spaces.
        - Collapses multiple consecutive spaces into a single space.

        The resulting string is easier to process and ensures a consistent format for further
        manipulation and analysis.

        :param amr: The AMR string to normalize.
        :type amr: str
        :return: The normalized AMR string.
        :rtype: str
        """
        re.sub("\r\n|\r|\n", " ", amr)
        amr = amr.replace("\r", " ").replace("\n", " ")
        amr = amr.strip()
        amr = amr.replace("(", " ( ")
        amr = amr.replace(")", " ) ")
        amr = amr.replace("/", " / ")
        amr = amr.replace("\t", " ")
        while "  " in amr:
            amr = amr.replace("  ", " ")
        return amr

    @staticmethod
    def strip_accents(amr: str) -> str:
        """
        Strips any accent marks from the given AMR string.

        :param amr: The AMR string to process.
        :type amr: str
        :return: The AMR string with accents removed.
        :rtype: str
        """
        return unidecode(amr)

    def get_nodes(self, relation: str, amr_list: list[str]) -> Node | None:
        """
        Retrieves nodes from the AMR string based on the provided top node relation.

        :param relation: The top node relation.
        :type relation: str
        :param amr_list: The array of words representing the AMR structure.
        :type amr_list: list[str]
        :return: The root node or None if an error occurs.
        :rtype: Node | None
        """
        if amr_list is None or len(amr_list) == 0:
            return None
        root = Node(var=amr_list[1], relation=relation)
        self.nodes.append(root)
        liv = 0
        i = 0
        while i < len(amr_list):
            word = amr_list[i]
            match word:
                case "(":
                    liv += 1
                    if liv == 2:
                        liv2 = 0
                        new_list = []
                        j = i
                        while j < len(amr_list):
                            word2 = amr_list[j]
                            match word2:
                                case "(":
                                    liv2 += 1
                                    new_list.append(word2)
                                case ")":
                                    liv2 -= 1
                                    new_list.append(word2)
                                    if liv2 == 0:
                                        root.add(self.get_nodes(amr_list[i - 1], new_list))
                                        i = j
                                        j = len(amr_list)
                                        liv -= 1
                                case _:
                                    new_list.append(word2)
                            j += 1
                case ")":
                    liv -= 1
                case "/":
                    for node in self.nodes:
                        if node.var == root.var and node.get_instance() is None:
                            node.make_equals(node=root)
                    root.add(Node(amr_list[i + 1], Glossary.INSTANCE))
                case _:
                    pass
                    try:
                        pass
                        if word[0] == ":" and len(amr_list) > i + 1 and amr_list[i + 1] != "(":
                            flag = False
                            for node in self.nodes:
                                if node.var == amr_list[i + 1]:
                                    new_node = node.get_copy(relation=word)
                                    root.add(new_node)
                                    self.nodes.append(new_node)
                                    flag = True
                                    break

                            if not flag:
                                new_node = Node(amr_list[i + 1], word)
                                root.add(new_node)
                                self.nodes.append(new_node)

                    except Exception as e:
                        logger.warning(e)
                        new_node = Node(amr_list[i + 1], word)
                        root.add(new_node)
                        self.nodes.append(new_node)
            i += 1
        if liv != 0:
            return None
        return root

    def check(self, root: Node) -> Node | None:
        """
        Recursively checks the status of nodes in the given root node and removes those that are not in an "OK" status.

        This method traverses the node list of the given root node, checking the status of each node. If a node's
        status is not "OK", it is removed from the list and added to a `removed` list. If the node has child nodes,
        the method is recursively applied to them as well. The method returns the updated root node, or `None` if the
        root node is not in an "OK" status.

        :param root: The root node to check and process.
        :type root: Node
        :return: The updated root node, or `None` if the root node's status is not "OK".
        :rtype: Node | None
        """
        if not isinstance(root, Node):
            return root
        if root.status != Glossary.NodeStatus.OK:
            return None
        for i, node in enumerate(root.node_list):
            if node.status != Glossary.NodeStatus.OK:
                self.removed.append(node)
                root.node_list.pop(i)
            else:
                root.node_list[i] = self.check(node)
        return root

    def parse(self, amr: str) -> Node:
        """
        Parses the given AMR string and returns the root node of the AMR representation.

        This method processes the AMR string in multiple stages:
            1. Strips accents from the input string.
            2. Retrieves the root node.
            3. Applies corrections for missing instances.
            4. Handles multi-sentence AMR representations.
            5. Translates relations and values into FRED format.
            6. Elaborates on verbs and resolves ambiguities.
            7. Adds the special TOPIC node if necessary.
            8. Corrects residual parsing errors.
            9. Integrates logical triples into the representation.

        :param amr: The AMR string to parse.
        :type amr: str
        :return: The root node of the parsed AMR.
        :rtype: Node
        """
        self.reinitialise()
        amr = self.strip_accents(amr)
        root = self.get_nodes(Glossary.TOP, self.string2array(amr))

        if root is not None:
            Parser.endless = 0
            Parser.endless2 = 0
            self.root_copy = root.get_copy(parser_nodes_copy=self.nodes_copy)
            if Parser.endless > Glossary.ENDLESS:
                self.root_copy = Node("Error", "Recursive")
                return root
        else:
            return Node("Error", "Root_is_None")

        root = self.check_missing_instances(root)

        # metodo per controllo multi sentence
        root = self.multi_sentence(root)

        # richiama il metodo che effettua la traduzione delle relazioni e dei valori
        root = self.fred_translate(root)

        # richiama il metodo che disambigua i verbi ed esplicita i ruoli dei predicati anonimi
        root = self.verbs_elaboration(root)

        # verifica la necessità di inserire il nodo speciale TOPIC
        root = self.topic(root)

        # verifica e tenta correzione errori residui
        root = self.residual(root)

        # AMR INTEGRATION
        root = self.logic_triples_integration(root)
        return root

    def fred_translate(self, root: Node) -> Node:
        """
        Translates the relations and values in the AMR string into FRED format.

        This method processes the root node and its children by applying several translation checks and transformations
        to convert AMR-specific relations and values into the corresponding FRED format. It handles various aspects,
        including operations, list verifications, inverses, modifiable relations, and instance elaborations.

        :param root: The root node of the AMR to be translated.
        :type root: Node
        :return: The root node after being processed and translated into FRED format.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        elif len(root.node_list) == 0:
            self.set_equals(root)  # verificare comportamento
            return root

        if Node.endless > Glossary.ENDLESS:
            return root

        for node in self.nodes:
            if node.get_instance() is not None:
                self.vars.append(node.var)

        root = self.dom_verify(root)

        # verifica ops
        root = self.control_ops(root)

        # verifica punti elenco
        root = self.li_verify(root)

        # verifica inversi
        root = self.inverse_checker(root)

        # verifica :mod
        root = self.mod_verify(root)

        # Elaborazione della lista dei nodi contenuti nel nodo attualmente in lavorazione
        root = self.list_elaboration(root)

        root = self.add_parent_list(root)

        # elaborazione del nodo figlio denominato instance in amr
        root = self.instance_elaboration(root)

        return root

    def check_missing_instances(self, root: Node) -> Node:
        """
        Checks for missing instances in the AMR and attempts to correct them.

        :param root: The root node of the AMR.
        :type root: Node
        :return: The root node after corrections, if necessary.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        if root.relation != Glossary.INSTANCE and root.get_instance() is None:
            for n in self.nodes:
                if n.var == root.var and n.get_instance() is not None:
                    root.make_equals(node=n)
            for i, node in enumerate(root.node_list):
                root.node_list[i] = self.check_missing_instances(node)
        return root

    def multi_sentence(self, root: Node) -> Node:
        """
        Handles multi-sentence cases in the AMR string.

        :param root: The root node of the AMR.
        :type root: Node
        :return: The root node after multi-sentence processing.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        if root.get_instance() is not None and root.get_instance().var == Glossary.AMR_MULTI_SENTENCE:
            sentences = root.get_snt()
            new_root = sentences.pop(0)
            new_root.relation = Glossary.TOP
            new_root.parent = None
            new_root.node_list += sentences
            for node in sentences:
                node.parent = new_root
                node.relation = Glossary.TOP
            return new_root
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.multi_sentence(node)
        return root

    def logic_triples_integration(self, root: Node) -> Node:
        """
        Integrates logical triples into the AMR representation.

        :param root: The root node of the AMR.
        :type root: Node
        :return: The root node with integrated logical triples.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root

        if root.status != Glossary.NodeStatus.OK:
            return root

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.logic_triples_integration(node)
        vis = False
        obj = root.relation
        for a in Glossary.AMR_INTEGRATION:
            if obj == Glossary.AMR + a[1:] and not a.endswith("_of"):
                rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
                rel.node_list.append(
                    Node(Glossary.PB_GENERICROLE + a[1:], Glossary.OWL_EQUIVALENT_PROPERTY, Glossary.NodeStatus.OK,
                         vis))
                rel.node_list.append(Node(Glossary.OWL_OBJECT_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                rel.node_list.append(
                    Node(Glossary.FS_SCHEMA_SEMANTIC_ROLE, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                root.add(rel)

            elif obj == Glossary.AMR + a[1:] and a.endswith("_of"):
                rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
                rel.node_list.append(
                    Node(Glossary.PB_GENERICROLE + a.substring(1).replace("_of", ""), Glossary.OWL_INVERSE_OF,
                         Glossary.NodeStatus.OK, vis))
                rel.node_list.append(Node(Glossary.OWL_OBJECT_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                rel.node_list.append(
                    Node(Glossary.FS_SCHEMA_SEMANTIC_ROLE, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
                root.add(rel)

        if (not obj.startswith(Glossary.FRED)
                and not obj.startswith(Glossary.RDFS)
                and not obj.startswith(Glossary.RDF)
                and not obj.startswith(Glossary.OWL)
                and not obj == Glossary.DUL_HAS_DATA_VALUE
                and not obj == Glossary.DUL_HAS_AMOUNT
                and not obj == Glossary.TOP):

            rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
            root.add(rel)
            rel.node_list.append(Node(Glossary.OWL_OBJECT_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))
        elif obj == Glossary.DUL_HAS_DATA_VALUE or obj == Glossary.DUL_HAS_AMOUNT:
            rel = Node(root.relation, Glossary.TOP, Glossary.NodeStatus.OK, vis)
            root.add(rel)
            rel.node_list.append(Node(Glossary.OWL_DATA_TYPE_PROPERTY, Glossary.RDF_TYPE, Glossary.NodeStatus.OK, vis))

        return root

    def set_equals(self, root: Node):
        """
        Sets the `var` attribute of nodes that are equal to the given root node.

        This method iterates over nodes that are considered equal to the given `root` node,
        and sets their `var` attribute to match the `var` attribute of the `root` node.

        :param root: The root node whose `var` value will be propagated to equal nodes.
        :type root: Node
        """
        if not isinstance(root, Node):
            return
        for node in self.get_equals(root):
            node.var = root.var

    def get_equals(self, root: Node) -> list[Node]:
        """
        Retrieves all nodes that are equal to the given root node.

        This method checks for equality between the `root` node and other nodes in the
        current context and returns a list of nodes that are considered equal to the root.

        :param root: The root node to compare against other nodes.
        :type root: Node
        :return: A list of nodes that are equal to the given root node.
        :rtype: list[Node]
        """
        if not isinstance(root, Node):
            return []
        return [node for node in self.nodes if node.__eq__(root)]

    def dom_verify(self, root: Node) -> Node:
        """
        Verifies and processes the AMR domain (`:domain`) for the given root node.

        This method checks if the root node has a `:domain` child and processes it
        according to specific rules. If a domain node is found, it adjusts its relation
        and variable name, assigns appropriate semantic roles, and updates the root node
        accordingly. The method also ensures recursive verification of all child nodes.

        :param root: The root node of the AMR structure to be verified.
        :type root: Node
        :return: The root node after domain verification.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        dom = root.get_child(Glossary.AMR_DOMAIN)
        if dom is not None:
            instance = root.get_instance()
            if instance is None:
                instance = self.get_instance_alt(root.get_node_id())
            self.topic_flag = False
            dom.relation = Glossary.TOP
            if dom.get_instance() is None and self.get_instance_alt(dom.get_node_id()) is not None:
                n_var = self.get_instance_alt(dom.get_node_id())
            elif dom.get_instance() is not None:
                n_var = dom.get_instance().var
            else:
                n_var = Glossary.FRED + dom.var.replace(Glossary.LITERAL, "")
            dom.var = n_var
            if instance is None:
                rel = Glossary.DUL_HAS_QUALITY
            elif instance.var in Glossary.ADJECTIVE:
                rel = Glossary.DUL_HAS_QUALITY
                self.treat_instance(root)
                root.var = Glossary.FRED + root.get_instance().var.capitalize()
            else:
                rel = Glossary.RDF_TYPE
                root.var = Glossary.FRED + instance.var.capitalize()
                self.remove_instance(root)
            new_node = root.get_copy(relation=rel)
            dom.node_list.append(new_node)
            self.nodes.append(new_node)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.dom_verify(node)
        return root

    def control_ops(self, root: Node) -> Node:
        """
        Verifies and processes operational (`:opX`) relations in the AMR structure.

        This method checks if the root node contains `:opX` relations and ensures they
        follow specific semantic rules.

        :param root: The root node of the AMR structure to be processed.
        :type root: Node
        :return: The root node after verifying and adjusting `:opX` relations.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        ins = root.get_instance()

        if isinstance(ins, Node) and (ins.var != Glossary.OP_NAME or ins.var != Glossary.FRED_MULTIPLE):
            return root
        ops_list = root.get_ops()
        if len(ops_list) > 0:
            for node in ops_list:
                assert isinstance(node, Node)
                if node.get_instance() is None:
                    if re.match(Glossary.NN_INTEGER, node.var):
                        node.relation = Glossary.DUL_HAS_DATA_VALUE
                        if (re.match(Glossary.NN_INTEGER, node.var)
                                and int(node.var) == 1
                                and root.get_child(Glossary.QUANT_HAS_QUANTIFIER) is None
                                and (ins is None or ins.var != Glossary.AMR_VALUE_INTERVAL)):
                            root.add(Node(Glossary.QUANT + Glossary.FRED_MULTIPLE, Glossary.QUANT_HAS_QUANTIFIER,
                                          Glossary.NodeStatus.OK))
                    else:
                        node.relation = Glossary.DUL_ASSOCIATED_WITH
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.control_ops(node)
        return root

    def li_verify(self, root: Node) -> Node:
        """
        Processes and verifies `:li` (list item) relations in the AMR structure.

        This method ensures that `:li` relations are properly handled by transforming them
        into a structured format. Recursively processes child nodes to ensure consistent list handling.

        :param root: The root node of the AMR structure to be processed.
        :type root: Node
        :return: The root node after verifying and adjusting `:li` relations.
        :rtype: Node
        """

        if not isinstance(root, Node):
            return root
        if root.relation == Glossary.AMR_LI:
            root.relation = Glossary.TOP
            var = root.parent.var
            new_instance = Node(Glossary.REIFI_HAVE_LI, Glossary.INSTANCE)
            self.nodes.append(new_instance)
            arg1 = Node(root.var, Glossary.AMR_ARG1)
            self.nodes.append(arg1)
            arg2 = Node(var, Glossary.AMR_ARG2)
            self.nodes.append(arg2)
            arg2.make_equals(root.parent)
            root.var = "li_" + str(root.get_node_id())
            root.add(new_instance)
            root.add(arg1)
            root.add(arg2)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.li_verify(node)
        return root

    def inverse_checker(self, root: Node) -> Node:
        """
        Identifies and processes inverse relations within the AMR structure.

        This method ensures that inverse relations (i.e., those ending with `-of`) are handled correctly.
        It performs the following operations:

        - Identifies nodes with inverse relations.
        - If the root node has a `:top` relation and only one inverse, it restructures the hierarchy.
        - Creates new nodes where necessary, ensuring proper relation consistency.
        - Adjusts parent-child relationships by reassigning inverse relations.
        - Recursively processes child nodes to handle all inverse relations.

        :param root: The root node of the AMR structure.
        :type root: Node
        :return: The root node after processing inverse relations.
        :rtype: Node
        """

        if not isinstance(root, Node):
            return root
        inv_nodes = root.get_inverses([])
        if len(inv_nodes) == 0:
            return root
        inv_nodes = root.get_inverses()
        if root.relation == Glossary.TOP and len(inv_nodes) == 1 and root.get_node_id() == 0:
            n = root.get_inverse()
            root.node_list.remove(n)
            root.relation = n.relation[0:-3]
            n.add(root)
            n.relation = Glossary.TOP
            return self.inverse_checker(n)
        else:
            for node in inv_nodes:
                new_node = root.get_copy(relation=node.relation[0:-3])
                if len(node.node_list) == 0 or (len(node.node_list) == 1 and node.get_instance() is not None):
                    ancestor = self.get_verb_ancestor(root)
                    new_parent = ancestor.get_copy(relation=Glossary.DUL_PRECEDES)
                    self.nodes.append(new_parent)
                    new_parent.set_status(Glossary.NodeStatus.AMR)
                    node.add(new_parent)
                self.nodes.append(new_node)
                node.relation = Glossary.TOP
                node.add(new_node)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.inverse_checker(node)
        return root

    def get_verb_ancestor(self, root: Node) -> Node | None:
        """
        Retrieves the closest verb ancestor of the given node.

        This method traverses up the node hierarchy to find the nearest ancestor
        whose instance matches a verb pattern defined in `Glossary.AMR_VERB2`.
        It follows these steps:

        - Starts from the given `root` node.
        - Moves up the hierarchy while the node ID is greater than 0 and the parent exists.
        - Checks if the parent's instance matches the AMR verb pattern.
        - Returns the first matching parent node or the last traversed node if no match is found.

        :param root: The node from which to start the search.
        :type root: Node
        :return: The nearest ancestor node that represents a verb, or None if none is found.
        :rtype: Node | None
        """

        node = root
        while node.get_node_id() > 0 and node.parent is not None:
            parent_ins = self.get_instance_alt(node.parent.get_node_id())
            if parent_ins is not None and re.match(Glossary.AMR_VERB2, parent_ins.var):
                return node.parent
            elif node.parent is not None:
                node = node.parent
        return node

    def mod_verify(self, root: Node) -> Node:
        """
        Verifies and adjusts modifier nodes in the AMR structure.

        This method processes modifier nodes (`:mod`) within the given `root` node, ensuring
        proper categorization and transformation based on their type. The verification
        involves:

        - Checking if the root instance is a verb, which influences modifier handling.
        - Identifying domain (`:domain`) and modifier (`:mod`) child nodes.
        - Handling cases where the modifier includes `:degree` and `:compared-to`,
          leading to instance modification.
        - Differentiating between adjectives, demonstratives, and other modifiers to assign
          the appropriate RDF/OWL relation (`dul:hasQuality`, `rdf:type`, etc.).
        - Ensuring correct subclass and association relationships for non-verb modifiers.

        :param root: The root node from which to start modifier verification.
        :type root: Node
        :return: The modified root node with verified and transformed modifiers.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        flag = True
        instance = self.get_instance_alt(root.get_node_id())
        if isinstance(instance, Node) and len(instance.var) > 3 and re.fullmatch(Glossary.AMR_VERB, instance.var[3:]):
            flag = False

        dom = root.get_child(Glossary.AMR_DOMAIN)
        mods = root.get_children(Glossary.AMR_MOD)

        for mod_node in mods:
            if isinstance(mod_node, Node) and flag:
                if isinstance(mod_node.get_instance(), Node):
                    mod_instance = mod_node.get_instance()
                elif isinstance(self.get_instance_alt(mod_node.get_node_id()), Node):
                    mod_instance = self.get_instance_alt(mod_node.get_node_id())
                else:
                    mod_instance = None
                if (mod_node.get_child(Glossary.AMR_DEGREE) is not None
                        and mod_node.get_child(Glossary.AMR_COMPARED_TO) is not None
                        and mod_instance is not None):
                    # caso :mod + :degree + :compared-to
                    instance.var = mod_instance.var + instance.var.capitalize()
                    self.remove_instance(mod_node)
                    root.node_list.remove(mod_node)
                    root.add_all(mod_node.node_list)
                elif (mod_instance is not None
                      and instance is not None
                      and not self.is_verb(mod_instance.var)
                      and mod_instance != Glossary.DISJUNCT
                      and mod_instance != Glossary.CONJUNCT
                      and mod_node.get_child(Glossary.AMR_NAME) is None):
                    if mod_node.get_instance() is not None:
                        mod_ins = mod_node.get_instance().var
                    else:
                        mod_ins = self.get_instance_alt(mod_node.get_node_id()).var
                    contains = mod_ins in Glossary.ADJECTIVE
                    demonstratives = " " + mod_ins + " " in Glossary.DEMONSTRATIVES
                    if contains:
                        mod_node.relation = Glossary.DUL_HAS_QUALITY
                        mod_node.var = Glossary.FRED + mod_ins.capitalize()
                        self.remove_instance(mod_node)
                    elif demonstratives:
                        mod_node.relation = Glossary.QUANT_HAS_DETERMINER
                        mod_node.var = Glossary.FRED + mod_ins.capitalize()
                        self.remove_instance(mod_node)
                    else:
                        if dom is None:
                            root_ins = instance.var
                            root.var = Glossary.FRED + root_ins.lower() + "_" + str(self.occurrence(root_ins))
                            self.remove_instance(root)
                            mod_node.var = (Glossary.FRED
                                            + mod_ins.replace(Glossary.FRED, "").capitalize()
                                            + root_ins.replace(Glossary.FRED, "").capitalize())
                            self.remove_instance(mod_node)
                            mod_node.relation = Glossary.RDF_TYPE
                            if mod_node.get_child(Glossary.RDFS_SUBCLASS_OF) is None:
                                mod_node.add(Node(Glossary.FRED + root_ins.replace(Glossary.FRED, "").capitalize(),
                                                  Glossary.RDFS_SUBCLASS_OF))
                            mod_node.add(Node(Glossary.FRED + (mod_ins.replace(Glossary.FRED, "")).capitalize(),
                                              Glossary.DUL_ASSOCIATED_WITH))
                        else:
                            root_ins = instance.var
                            root.var = (Glossary.FRED + mod_ins.replace(Glossary.FRED, "").capitalize()
                                        + root_ins.replace(Glossary.FRED, ""))
                            instance.var = root.var
                            self.remove_instance(root)
                            mod_node.var = Glossary.FRED + mod_ins.replace(Glossary.FRED, "").capitalize()
                            mod_node.relation = Glossary.DUL_ASSOCIATED_WITH
                            self.remove_instance(mod_node)
                            if root.get_child(Glossary.RDFS_SUBCLASS_OF) is None:
                                root.add(Node(Glossary.FRED + root_ins.replace(Glossary.FRED, "").capitalize(),
                                              Glossary.RDFS_SUBCLASS_OF))
                    mod_node.set_status(Glossary.NodeStatus.OK)
            elif mod_node is not None and not flag:
                if mod_node.get_instance() is not None:
                    mod_ins = mod_node.get_instance().var
                else:
                    mod_ins = self.get_instance_alt(mod_node.get_node_id()).var
                contains = mod_ins in Glossary.ADJECTIVE
                demonstratives = " " + mod_ins + " " in Glossary.DEMONSTRATIVES
                if contains:
                    mod_node.relation = Glossary.DUL_HAS_QUALITY
                    mod_node.var = Glossary.FRED + mod_ins.capitalize()
                    self.remove_instance(mod_node)
                elif demonstratives:
                    mod_node.relation = Glossary.QUANT_HAS_DETERMINER
                    mod_node.var = Glossary.FRED + mod_ins.capitalize()
                    self.remove_instance(mod_node)
                else:
                    mod_node.var = Glossary.FRED + mod_ins.replace(Glossary.FRED, "").capitalize()
                    mod_node.relation = Glossary.DUL_ASSOCIATED_WITH
                    self.remove_instance(mod_node)
                mod_node.set_status(Glossary.NodeStatus.OK)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.mod_verify(node)

        return root

    def list_elaboration(self, root: Node) -> Node:
        """
        Processes an Abstract Meaning Representation (AMR) tree by refining its structure,
        updating node relations, and handling specific linguistic constructs.

        This method applies various transformations and normalizations to the nodes of the input
        AMR tree, modifying their relations, variables, and statuses based on predefined rules.
        It ensures consistency in the representation and resolves linguistic constructs such as
        coordination, date intervals, pronouns, demonstratives, and modality markers.

        The function performs the following operations:

        - Calls `root_elaboration`, `date_entity`, and `prep_control` to preprocess the root node.
        - Iterates through the child nodes (`node_list`) and applies transformation rules.
        - Handles special cases such as:

            - Converting Wikidata links.
            - Processing negation, modality, and polarity markers.
            - Handling personal pronouns and demonstratives.
            - Normalizing names and entity references.
            - Adjusting relations for AMR constructs like `:quant`, `:age`, and `:degree`.
            - Ensuring RDF/OWL compliance where necessary.

        - Updates `self.to_add` with new nodes when required.

        :param root: The root node of the AMR tree to be processed.
        :type root: Node
        :return: The transformed AMR tree with updated nodes and relations.
        :rtype: Node
        """
        if not isinstance(root, Node) or len(root.node_list) == 0:
            return root

        root = self.root_elaboration(root)
        root = self.date_entity(root)
        root = self.prep_control(root)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.prep_control(node)

            if node.relation == Glossary.AMR_WIKIDATA:
                if node.var == Glossary.AMR_MINUS:
                    node.relation = ""
                    node.status = Glossary.NodeStatus.REMOVE
                else:
                    node.relation = Glossary.OWL_SAME_AS
                    node.var = Glossary.WIKIDATA + node.var
                    node.status = Glossary.NodeStatus.OK

            if node.relation == Glossary.PREP_SUBSTITUTION:
                node.status = Glossary.NodeStatus.REMOVE
                self.to_add += node.node_list

            if node.relation == Glossary.AMR_POLARITY_OF:
                node.relation = Glossary.AMR + Glossary.AMR_POLARITY_OF[1:]

            if (node.relation == Glossary.AMR_DOMAIN and node.get_instance() is not None
                    and " " + node.get_instance().var + " " in Glossary.DEMONSTRATIVES):
                self.topic_flag = False
                node.relation = Glossary.QUANT_HAS_DETERMINER
                node.var = Glossary.FRED + node.get_instance().var.capitalize()
                self.remove_instance(node)
                node.status = Glossary.NodeStatus.OK

            node_instance = node.get_instance()

            # "OR" and "AND" cases with ":OPS"
            if node_instance is not None and (node_instance.var == Glossary.OR or node_instance.var == Glossary.AND):
                if node_instance.var == Glossary.AND:
                    node_instance.var = Glossary.CONJUNCT
                else:
                    node_instance.var = Glossary.DISJUNCT
                ops = node.get_ops()
                for n in ops:
                    n.relation = Glossary.DUL_HAS_MEMBER

            # "date-interval" case with ":op" list
            if node_instance is not None and node_instance.var == Glossary.AMR_DATE_INTERVAL:
                ops = node.get_ops()
                for n in ops:
                    n.relation = Glossary.DUL_HAS_MEMBER

            # special cases with personal pronouns and demonstrative adjectives
            if node.var in Glossary.PERSON:
                node.var = Glossary.FRED_PERSON
                # self.set_equals(root)
                root.prefix = True

            if node.relation == Glossary.AMR_NAME:
                root.prefix = True
                if root.get_poss() is not None and root.get_instance() is not None:
                    root.get_poss().relation = root.get_instance().var.replace(Glossary.FRED, "") + Glossary.OF

            if (node.relation == Glossary.AMR_NAME and node_instance is not None
                    and node_instance.var == Glossary.OP_NAME
                    and len(node.get_ops()) > 0
                    and not self.check_for_amr_instances(root)):
                ops = node.get_ops()
                name = ""
                for n in ops:
                    name += Glossary.OP_JOINER + n.var
                    node.node_list.remove(n)
                name = Glossary.LITERAL + name[1:].replace(Glossary.LITERAL, "")
                node.var = name
                node.relation = Glossary.SCHEMA + Glossary.OP_NAME
                self.treat_instance(node)
            elif (node.relation == Glossary.AMR_NAME and node_instance is not None
                  and node_instance.var == Glossary.OP_NAME
                  and len(node.get_ops()) > 0
                  and self.check_for_amr_instances(root)):
                ops = node.get_ops()
                name = ""
                for n in ops:
                    name += Glossary.OP_JOINER + n.var
                    node.node_list.remove(n)
                name = Glossary.LITERAL + name[1:].replace(Glossary.LITERAL, "")
                node.var = name
                node.relation = Glossary.SCHEMA + Glossary.OP_NAME
                self.treat_instance(node)
                self.remove_instance(node)
            elif (node_instance is not None and node_instance.var == Glossary.OP_NAME
                  and len(node.get_ops()) > 0
                  and not self.check_for_amr_instances(root)):
                ops = node.get_ops()
                name = ""
                for n in ops:
                    name += Glossary.OP_JOINER + n.var
                    node.node_list.remove(n)
                name = Glossary.LITERAL + name[1:].replace(Glossary.LITERAL, "")
                node.var = name
                self.treat_instance(node)

            if node.relation == Glossary.AMR_WIKI:
                if node.var == Glossary.AMR_MINUS:
                    node.status = Glossary.NodeStatus.REMOVE
                else:
                    node.relation = Glossary.OWL_SAME_AS
                    node.var = Glossary.DBPEDIA + node.var
                    node.status = Glossary.NodeStatus.OK

            elif node.relation == Glossary.AMR_MODE and (node.var == Glossary.AMR_IMPERATIVE
                                                         or node.var == Glossary.AMR_EXPRESSIVE
                                                         or node.var == Glossary.AMR_INTERROGATIVE):
                node.relation = Glossary.AMR + node.relation[1:]
                node.var = Glossary.AMR + node.var.replace(":", "")

            elif node.relation == Glossary.AMR_POLITE:
                if node.var != Glossary.AMR_PLUS:
                    node.add(Node(Glossary.BOXING_FALSE, Glossary.BOXING_HAS_TRUTH_VALUE, Glossary.NodeStatus.OK))
                node.var = Glossary.AMR + node.relation[1:]
                node.relation = Glossary.BOXING_HAS_MODALITY
                node.add(Node(Glossary.DUL_HAS_QUALITY, Glossary.RDFS_SUB_PROPERTY_OF, Glossary.NodeStatus.OK))

            elif (node.relation == Glossary.AMR_POLARITY
                  and node_instance is not None
                  and node_instance.var == Glossary.AMR_UNKNOWN):
                node.relation = Glossary.BOXING_HAS_TRUTH_VALUE
                node.var = Glossary.BOXING_UNKNOWN
                self.remove_instance(node)

            elif node_instance is not None and node_instance.var == Glossary.AMR_UNKNOWN:
                node.var = Glossary.OWL_THING
                self.remove_instance(node)
                if node.relation == Glossary.AMR_QUANT:
                    node.relation = Glossary.AMR + Glossary.AMR_QUANT[1:]

            elif " " + node.var + " " in Glossary.MALE:
                node.var = Glossary.FRED_MALE
                self.set_equals(root)

            elif " " + node.var + " " in Glossary.FEMALE:
                node.var = Glossary.FRED_FEMALE
                self.set_equals(root)

            elif " " + node.var + " " in Glossary.THING:
                node.var = Glossary.FRED_NEUTER
                node.add(Node(Glossary.OWL_THING, Glossary.RDF_TYPE, Glossary.NodeStatus.OK))
                self.set_equals(root)
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == Glossary.AMR_POSS and self.get_instance_alt(root.get_node_id()) is not None:
                node.relation = (Glossary.FRED
                                 + self.get_instance_alt(root.get_node_id()).var.replace(Glossary.FRED, "")
                                 + Glossary.OF)
                node.set_status(Glossary.NodeStatus.OK)

            elif ((node.relation == Glossary.AMR_QUANT or node.relation == Glossary.AMR_FREQUENCY)
                  and re.match(Glossary.NN_INTEGER, node.var) and node_instance is None):
                node.relation = Glossary.DUL_HAS_DATA_VALUE
                if ((re.match(Glossary.NN_INTEGER, node.var) and not int(node.var) == 1)
                        or not re.match(Glossary.NN_INTEGER, node.var)):
                    self.to_add.append(Node(Glossary.QUANT + Glossary.FRED_MULTIPLE,
                                            Glossary.QUANT_HAS_QUANTIFIER,
                                            Glossary.NodeStatus.OK))
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == (Glossary.AMR_QUANT and node_instance is not None
                                   and re.match(Glossary.AMR_QUANTITY, node_instance.var)):
                ops = node.get_ops()
                for n in ops:
                    node.node_list.remove(n)
                    n.relation = Glossary.DUL_HAS_DATA_VALUE
                    self.to_add.append(n)
                    n.set_status(Glossary.NodeStatus.OK)
                node.relation = Glossary.QUANT_HAS_QUANTIFIER
                if node_instance.var == Glossary.FRED_MULTIPLE:
                    node.var = Glossary.QUANT + Glossary.FRED_MULTIPLE
                    self.remove_instance(node)
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == Glossary.AMR_QUANT_OF and node_instance is not None:
                node.relation = Glossary.FRED + self.get_instance_alt(root.get_node_id()).var + Glossary.OF
                node.set_status(Glossary.NodeStatus.OK)

            elif node.relation == Glossary.AMR_AGE and root.get_instance() is not None and node_instance is None:
                age = node.var
                node.relation = Glossary.TOP
                node.var = Glossary.NEW_VAR + str(self.occurrence(Glossary.NEW_VAR))
                node.add(Node(Glossary.AGE_01, Glossary.INSTANCE))
                n1 = root.get_copy(relation=Glossary.AMR_ARG1)
                self.nodes.append(n1)
                node.add(n1)
                node.add(Node(age, Glossary.AMR_ARG2))
                root.node_list[i] = self.list_elaboration(node)

            elif node.relation == Glossary.AMR_AGE and root.get_instance() is not None and node_instance is not None:
                node.relation = Glossary.TOP
                n1 = root.get_copy(relation=Glossary.AMR_ARG1)
                self.nodes.append(n1)
                new_age_node = Node(Glossary.NEW_VAR + str(self.occurrence(Glossary.NEW_VAR)), Glossary.AMR_ARG2)
                self.nodes.append(new_age_node)
                new_age_node.add_all(node.node_list)
                node.node_list = []
                node.add(n1)
                node.var = Glossary.NEW_VAR + str(self.occurrence(Glossary.NEW_VAR))
                node.add(Node(Glossary.AGE_01, Glossary.INSTANCE))
                node.add(new_age_node)
                root.node_list[i] = self.list_elaboration(node)

            elif node.relation == (Glossary.AMR_DEGREE and node_instance is not None
                                   and not self.is_verb(node_instance.var)):
                node.var = Glossary.FRED + node_instance.var.capitalize()
                self.remove_instance(node)

            elif node.relation == (Glossary.AMR_MANNER and node_instance is not None
                                   and not self.is_verb(node_instance.var)):
                if re.match(Glossary.AMR_VERB2, node_instance.var) or len(self.manner_adverb(node_instance.var)) > 0:
                    if (re.match(Glossary.AMR_VERB2, node_instance.var) and len(
                            self.manner_adverb(node_instance.var[0:-3]))) > 0:
                        node.var = Glossary.FRED + self.manner_adverb(node_instance.var[0:-3]).capitalize()
                    elif len(self.manner_adverb(node_instance.var)) > 0:
                        node.var = Glossary.FRED + self.manner_adverb(node_instance.var).capitalize()
                    else:
                        node.var = Glossary.FRED + node_instance.var[0:-3].capitalize()
                    self.remove_instance(node)
                else:
                    node.relation = Glossary.AMR + Glossary.AMR_MANNER[1:]

            elif (node.relation == Glossary.AMR_MANNER and node_instance is not None and root.get_instance() is not None
                  and self.is_verb(node_instance.var)):
                node.relation = Glossary.FRED + root.get_instance().var[:-3] + Glossary.BY

            elif node.relation.startswith(Glossary.AMR_PREP):
                node.relation = node.relation.replace(Glossary.AMR_PREP, Glossary.FRED)

            elif (node.relation == Glossary.AMR_PART_OF or node.relation == Glossary.AMR_CONSIST_OF
                  and node_instance is not None):
                node.relation = node.relation.replace(Glossary.AMR_RELATION_BEGIN, Glossary.AMR)

            elif node.relation == Glossary.AMR_EXTENT and node_instance is not None:
                node.var = Glossary.FRED + node_instance.var.capitalize()
                self.remove_instance(node)

            if node.relation == Glossary.AMR_VALUE and node_instance is None:
                if re.match(Glossary.NN_INTEGER2, node.var) or re.match(Glossary.NN_INTEGER, node.var):
                    node.relation = Glossary.DUL_HAS_DATA_VALUE
                else:
                    node.relation = Glossary.DUL_HAS_QUALITY
                    node.var = Glossary.FRED + node.var.capitalize()

            if node.relation == Glossary.AMR_CONJ_AS_IF:
                node.relation = Glossary.FRED_AS_IF
                node.set_status(Glossary.NodeStatus.OK)

            if node.relation == Glossary.AMR_CONDITION:
                node.relation = Glossary.DUL_HAS_PRECONDITION

            if node.status != Glossary.NodeStatus.REMOVE:
                for j, relation in enumerate(Glossary.AMR_RELATIONS):
                    if node.relation == relation and re.match(Glossary.AMR_VARS[j], node.var):
                        if len(Glossary.FRED_RELATIONS[j]) > 0:
                            node.relation = Glossary.FRED_RELATIONS[j]
                        if len(Glossary.FRED_VARS[j]) > 0:
                            node.var = Glossary.FRED_VARS[j]
                    node.set_status(Glossary.NodeStatus.OK)

            ops = node.get_ops()
            if len(ops) > 0:
                for n1 in ops:
                    node.node_list.remove(n1)
                    n1.relation = node.relation
                    self.to_add.append(n1)
                node.relation = Glossary.DUL_ASSOCIATED_WITH
                new_node = Node("", "")
                new_node.substitute(node)
                node.set_status(Glossary.NodeStatus.REMOVE)
                self.nodes.append(new_node)
                ops[0].add(new_node)

            if node.status == Glossary.NodeStatus.REMOVE:
                self.removed.append(node)

            if node.relation.startswith(Glossary.AMR_RELATION_BEGIN) and node.status != Glossary.NodeStatus.REMOVE:
                node.set_status(Glossary.NodeStatus.AMR)
            elif node.status != Glossary.NodeStatus.REMOVE:
                node.set_status(Glossary.NodeStatus.OK)

        root.node_list[:] = [node for node in root.node_list if node.status != Glossary.NodeStatus.REMOVE]

        if len(self.to_add) > 0:
            root.add_all(self.to_add)
            self.to_add = []
            root = self.list_elaboration(root)

        if root.relation == Glossary.TOP and len(root.get_ops()) > 0:
            ops = root.get_ops()
            for op in ops:
                root.node_list.remove(op)
            new_root = Node("", "")
            new_root.substitute(root)
            new_root.relation = Glossary.DUL_ASSOCIATED_WITH
            self.nodes.append(new_root)
            root.substitute(ops[0])
            root.add(new_root)
            root.relation = Glossary.TOP
            for op in ops:
                op.relation = Glossary.TOP
                if not root.__eq__(op):
                    root.add(op)

            if root.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                root.set_status(Glossary.NodeStatus.AMR)
            else:
                root.set_status(Glossary.NodeStatus.OK)

        if Node.endless2 > Glossary.ENDLESS2:
            return root

        for i, node in enumerate(root.node_list):
            Node.endless2 += 1
            root.node_list[i] = self.list_elaboration(node)

        return root

    def add_parent_list(self, root: Node) -> Node:
        """
        Recursively updates the given AMR tree by ensuring that all parent nodes
        referenced in `parent_list` are included in the main `node_list`.

        This method identifies nodes with non-empty `parent_list` and verifies whether
        their parent nodes are already present in `root.node_list`. If a parent node
        is missing, it is added to maintain structural consistency. The function then
        recursively applies this process to all child nodes.

        :param root: The root node of the AMR tree to be processed.
        :type root: Node
        :return: The updated AMR tree with parent nodes properly integrated.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        to_add = root.get_nodes_with_parent_list_not_empty()
        if len(to_add) != 0:
            for node in to_add:
                for node_1 in node.parent_list:
                    flag = False
                    for node_2 in root.node_list:
                        if node_1.relation == node_2.relation and node_1.var == node_2.var:
                            flag = True
                    if not flag:
                        root.node_list.append(node_1)
                root.node_list.remove(node)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.add_parent_list(node)
        return root

    def instance_elaboration(self, root: Node) -> Node:
        """
        Processes an AMR (Abstract Meaning Representation) tree node to refine its instance representation,
        adjust its status, and classify it based on predefined linguistic patterns.

        This method ensures proper handling of AMR instances by:
        - Updating the status of nodes based on their relation type.
        - Identifying verb instances and adjusting their representation.
        - Modifying instance variables and assigning appropriate types.
        - Recursively processing child nodes.

        :param root: The root node of the AMR tree to be processed.
        :type root: Node
        :return: The updated AMR tree with refined instance handling.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        if root.status == Glossary.NodeStatus.OK and root.relation.startswith(
                Glossary.AMR_RELATION_BEGIN) and root.relation != Glossary.TOP:
            root.set_status(Glossary.NodeStatus.AMR)
            return root

        if root.status != Glossary.NodeStatus.OK and root.relation.startswith(
                Glossary.AMR_RELATION_BEGIN) and root.relation != Glossary.TOP:
            root.set_status(Glossary.NodeStatus.OK)

        instance = root.get_instance()
        if isinstance(instance, Node):
            if len(instance.var) > 3 and re.match(Glossary.AMR_VERB, instance.var[-3:]):
                if self.is_verb(instance.var):
                    root.node_type = Glossary.NodeType.VERB
                    self.topic_flag = False
                    instance.add(Node(Glossary.DUL_EVENT, Glossary.RDFS_SUBCLASS_OF, Glossary.NodeStatus.OK))
                if root.status == Glossary.NodeStatus.OK:
                    root.node_type = Glossary.NodeType.VERB
                    self.topic_flag = False

                root.var = Glossary.FRED + instance.var[0:-3] + "_" + str(self.occurrence(instance.var[0:-3]))
                instance.relation = Glossary.RDF_TYPE
                root.verb = Glossary.ID + instance.var.replace('-', '.')
                self.args(root)
                instance.var = Glossary.PB_ROLESET + instance.var

                if not instance.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    instance.status = Glossary.NodeStatus.OK
                else:
                    instance.status = Glossary.NodeStatus.AMR

                if not root.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    root.status = Glossary.NodeStatus.OK
                else:
                    root.status = Glossary.NodeStatus.AMR
            else:
                root = self.other_instance_elaboration(root)
                if not root.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    root.status = Glossary.NodeStatus.OK
                else:
                    root.status = Glossary.NodeStatus.AMR

            for node in self.nodes:
                if root.__eq__(node):
                    node.var = root.var

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.instance_elaboration(node)

        return root

    def verbs_elaboration(self, root: Node) -> Node:
        """
        Elaborates on verbs and resolves ambiguities for predicate arguments.

        :param root: The root node of the AMR.
        :type root: Node
        :return: The root node after verb elaboration.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        lemma = root.verb
        if root.node_type == Glossary.NodeType.VERB:
            pb = Propbank.get_propbank()
            lemma2 = lemma[3:].replace(".", "-")
            roles = pb.frame_find(Glossary.PB_ROLESET + lemma2, Glossary.PropbankFrameFields.PB_Frame)
            if len(roles) > 0:
                label = roles[0][Glossary.PropbankFrameFields.PB_FrameLabel.value]
                if len(label) > 0 and isinstance(root.get_child(Glossary.RDF_TYPE), Node):
                    root.get_child(Glossary.RDF_TYPE).add(Node(label, Glossary.RDFS_LABEL, Glossary.NodeStatus.OK))
                new_nodes_vars = []
                for line in roles:
                    fn_frame = line[Glossary.PropbankFrameFields.FN_Frame.value]
                    if fn_frame is not None and len(fn_frame) > 0 and fn_frame not in new_nodes_vars:
                        new_nodes_vars.append(fn_frame)
                    va_frame = line[Glossary.PropbankFrameFields.VA_Frame.value]
                    if va_frame is not None and len(va_frame) > 0 and va_frame not in new_nodes_vars:
                        new_nodes_vars.append(va_frame)

                type_node = root.get_child(Glossary.RDF_TYPE)
                if isinstance(type_node, Node):
                    for var in new_nodes_vars:
                        new_node = Node(var, Glossary.FS_SCHEMA_SUBSUMED_UNDER, Glossary.NodeStatus.OK)
                        type_node.add(new_node)
                        new_node.visibility = False

                # search for roles
                for node in root.get_args():
                    if isinstance(node, Node):
                        r = Glossary.PB_ROLESET + lemma2

                        pb_roles = pb.role_find(r,
                                                Glossary.PropbankRoleFields.PB_Frame,
                                                Glossary.PB_SCHEMA + node.relation[1:].upper(),
                                                Glossary.PropbankRoleFields.PB_ARG)

                        if (len(pb_roles) > 0
                                and pb_roles[0][Glossary.PropbankRoleFields.PB_Role.value] is not None
                                and len(pb_roles[0][Glossary.PropbankRoleFields.PB_Role.value]) > 0):
                            node.relation = pb_roles[0][Glossary.PropbankRoleFields.PB_Role.value]
                        node.status = Glossary.NodeStatus.OK

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.verbs_elaboration(node)
        return root

    def topic(self, root: Node) -> Node:
        """
        Determines if a special topic node needs to be added to the AMR.

        :param root: The root node of the AMR.
        :type root: Node
        :return: The root node after topic handling.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        if self.topic_flag:
            root.add(Node(Glossary.FRED_TOPIC, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK))
        return root

    def residual(self, root: Node) -> Node:
        """
        Attempts to correct residual errors in the parsed AMR.

        :param root: The root node of the AMR.
        :type root: Node
        :return: The root node after error correction.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        # print(root)
        if Glossary.LITERAL in root.var:
            root.var = root.var.replace(Glossary.LITERAL, "")
            root.set_status(Glossary.NodeStatus.OK)

        if Glossary.NON_LITERAL not in root.var and len(root.node_list) == 1:
            var = root.var
            root_id = root.get_node_id()
            child = root.node_list[0]
            if Glossary.NON_LITERAL in child.var and child.relation == Glossary.DUL_ASSOCIATED_WITH:
                root.var = child.var
                root.add_all(child.node_list)
                root.make_equals(child)
                child.make_equals(node_id=root_id)
                child.node_list = []
                child.var = var

        if Glossary.FRED + Glossary.LITERAL2 in root.var:
            root.var = root.var.replace(Glossary.FRED + Glossary.LITERAL2, "")
            root.set_status(Glossary.NodeStatus.OK)

        if Glossary.FRED in root.var or Glossary.AMR in root.var:
            temp = root.var.replace(Glossary.FRED, "").replace(Glossary.AMR, "")
            temp = self.disambiguation(temp)
            root.var = temp

        if "fred:Fred:" in root.var:
            root.var = root.var.replace("fred:Fred:", "")
            root.var = Glossary.FRED + root.var.capitalize()

        if re.match(Glossary.AMR_VERB2, root.var) and root.status != Glossary.NodeStatus.OK and len(root.var) > 3:
            root.add(Node(Glossary.DUL_EVENT, Glossary.RDFS_SUBCLASS_OF, Glossary.NodeStatus.OK))
            args = root.get_args()
            if Glossary.NON_LITERAL in root.var:
                verb = root.var.split(Glossary.NON_LITERAL)[1]
            else:
                verb = root.var

            for arg in args:
                arg.verb = verb
            root.var = root.var[0:-3]
            root.node_type = Glossary.NodeType.VERB

        elif re.match(Glossary.AMR_VERB2, root.var) and root.status != Glossary.NodeStatus.OK:
            if Glossary.NON_LITERAL in root.var:
                new_var = root.var.split(Glossary.NON_LITERAL)[1].lower()
            else:
                new_var = root.var

            root.malformed = True
            root.add(Node(Glossary.FRED + new_var[0:-3].capitalize(), Glossary.RDF_TYPE, Glossary.NodeStatus.OK))
            root.var = Glossary.FRED + new_var[0:-3] + "_" + str(self.occurrence(new_var[0:-3]))
            self.set_equals(root)

        if re.match(Glossary.AMR_ARG, root.relation):
            root.relation = Glossary.VN_ROLE_PREDICATE
            root.malformed = True
            root.set_status(Glossary.NodeStatus.OK)

        if root.relation == Glossary.AMR_COMPARED_TO:
            new_relation = Glossary.AMR + Glossary.AMR_COMPARED_TO
            root.relation = new_relation
            root.set_status(Glossary.NodeStatus.OK)

        if (root.relation == Glossary.AMR_MODE and (root.var == Glossary.AMR_IMPERATIVE
                                                    or root.var == Glossary.AMR_EXPRESSIVE
                                                    or root.var == Glossary.AMR_INTERROGATIVE)):
            root.relation = Glossary.AMR + root.relation[1:]
            root.var = Glossary.AMR + root.var.replace(":", "")
            root.set_status(Glossary.NodeStatus.OK)

        if root.relation == Glossary.AMR_CONSIST_OF or root.relation == Glossary.AMR_UNIT:
            root.relation = root.relation.replace(":", Glossary.AMR)
            root.set_status(Glossary.NodeStatus.OK)

        if root.relation.startswith(Glossary.NON_LITERAL):
            root.relation = root.relation.replace(Glossary.NON_LITERAL, Glossary.AMR)
            if (Glossary.NON_LITERAL not in root.var and root.status != Glossary.NodeStatus.OK
                    and Glossary.FRED not in root.var):
                root.var = Glossary.FRED + root.var.capitalize()
            root.set_status(Glossary.NodeStatus.OK)

        if root.var == Glossary.AMR_MINUS and root.relation == Glossary.PBLR_POLARITY:
            root.var = Glossary.FRED + "Negative"

        for node in root.node_list:
            if Glossary.NON_LITERAL not in node.var and node.var in self.vars:
                node.var = Glossary.FRED + "malformed_amr/" + node.var
                node.malformed = True

        root.node_list[:] = [n for n in root.node_list if n.status != Glossary.NodeStatus.REMOVE]

        if Glossary.NON_LITERAL not in root.var and re.match(Glossary.AMR_VAR, root.var):
            root.var = Glossary.FRED + "Undefined"
            root.malformed = True

        if root.var.count(Glossary.NON_LITERAL) > 1:
            root.var = ":".join(root.var.split(Glossary.NON_LITERAL)[-2:])

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.residual(node)

        return root

    def get_instance_alt(self, node_id) -> Node | None:
        """
        Get the instance associated with the given node ID, if it exists.

        :param node_id: The ID of the node whose instance is to be retrieved.
        :type node_id: int
        :return: The instance associated with the node, or None if no instance is found.
        :rtype: Node or None
        """
        for node in self.nodes_copy:
            if node.get_node_id() == node_id and node.get_instance() is not None:
                return node.get_instance()
        return None

    def treat_instance(self, root: Node):
        """
            Process and modify the given root node's instance and update all equal nodes.

            This method updates the `var` of all nodes that are equal to the root node
            and changes the status of the instance associated with the root node to REMOVE.

            :param root: The root node to be treated.
            :type root: Node
            """
        if not isinstance(root, Node):
            return
        for node in self.get_equals(root):
            node.var = root.var
        if root.get_instance() is not None:
            root.get_instance().status = Glossary.NodeStatus.REMOVE

    def remove_instance(self, root: Node):
        """
        Remove the instance associated with the given root node.

        This method updates the `var` of all nodes equal to the root node and removes
        the instance from the node list of the root node.

        :param root: The root node from which the instance should be removed.
        :type root: Node
        """
        if not isinstance(root, Node):
            return
        for node in self.get_equals(root):
            node.var = root.var
        if root.get_instance() is not None:
            root.node_list.remove(root.get_instance())

    @staticmethod
    def is_verb(var, node_list: list[Node] | None = None) -> bool:
        """
        Check if the provided variable corresponds to a verb.

        This method checks if the given variable represents a verb by either searching
        Propbank frames or by checking a list of nodes if provided.

        :param var: The variable (usually a string) to be checked.
        :type var: str
        :param node_list: Optional list of nodes to search through (only used if `var` is a string).
        :type node_list: list of Node, optional
        :return: True if the variable corresponds to a verb, False otherwise.
        :rtype: bool
        """
        prb = Propbank.get_propbank()
        if node_list is None and isinstance(var, str):
            result = prb.frame_find(Glossary.PB_ROLESET + var, Glossary.PropbankFrameFields.PB_Frame)
            return result is not None and len(result) > 0
        elif isinstance(var, str) and isinstance(node_list, list):
            result = prb.list_find(var, node_list)
            return result is not None and len(result) > 0

    def occurrence(self, word: str) -> int:
        """
        Calculate and update the occurrence count of a given word.

        This method updates the occurrence count of the word in the `couples` list
        and appends a new entry if the word is not already present.

        :param word: The word whose occurrence is to be calculated.
        :type word: str
        :return: The updated occurrence count for the word.
        :rtype: int
        """
        occurrence_num = 1
        for couple in self.couples:
            if word == couple.get_word():
                occurrence_num += couple.get_occurrence()
                couple.set_occurrence(occurrence_num)
        if occurrence_num == 1:
            self.couples.append(Couple(1, word))
        return occurrence_num

    @staticmethod
    def args(root: Node):
        """
        Process the arguments of the given root node and update the related nodes.

        This method iterates through the `node_list` of the root node, and if any
        node's relation matches the pattern defined in `Glossary.AMR_ARG`, it assigns
        the root's verb to the node.

        :param root: The root node whose arguments are to be processed.
        :type root: Node
        :return: None
        """
        if not isinstance(root, Node):
            return root
        for node in root.node_list:
            if re.match(Glossary.AMR_ARG, node.relation):
                node.verb = root.verb

    def other_instance_elaboration(self, root: Node) -> Node:
        """
        Elaborate on instances other than verbs related to the given root node.

        This method retrieves the instance associated with the root node and, based
        on its properties, generates a new variable for the instance, updates its
        relation, and assigns specific values to the instance based on predefined
        glossaries. It also modifies nodes that are equal to the root node.

        :param root: The root node to be processed.
        :type root: Node
        :return: The modified root node.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        instance = root.get_instance()
        if not isinstance(instance, Node):
            return root

        n_var = Glossary.FRED + instance.var + "_" + str(self.occurrence(instance.var))
        for node in self.get_equals(root):
            ins = node.get_instance()
            if isinstance(ins, Node):
                node.var = n_var
                ins.relation = Glossary.RDF_TYPE
                flag = True
                if instance.var in Glossary.SPECIAL_INSTANCES:
                    ins.var = (Glossary.SPECIAL_INSTANCES_PREFIX[Glossary.SPECIAL_INSTANCES.index(instance.var)]
                               + instance.var.capitalize())
                    flag = False

                if instance.var in Glossary.AMR_INSTANCES and root.prefix:
                    ins.var = Glossary.AMR + instance.var.capitalize()
                    flag = False

                if instance.var in Glossary.AMR_ALWAYS_INSTANCES:
                    ins.var = Glossary.AMR + instance.var.capitalize()
                    flag = False

                if flag:
                    ins.var = Glossary.FRED + instance.var.capitalize()

                if ins.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    ins.status = Glossary.NodeStatus.OK
            else:
                node.var = n_var
        return root

    def root_elaboration(self, root: Node) -> Node:
        """
        Elaborate on the given root node by processing its instance and its children.

        This method performs various transformations on the root node and its associated instance.
        It checks for specific conditions in the node and its children, modifying relationships,
        variables, and adding new nodes based on predefined glossaries and logical rules. The method
        also handles special cases like conjunctions, disjunctions, concessions, and conditions.

        :param root: The root node to be processed and elaborated.
        :type root: Node
        :return: The modified root node after elaboration.
        :rtype: Node
        """
        instance = self.get_instance_alt(root.get_node_id())
        root_instance = root.get_instance()

        if root_instance is not None and (root_instance.var == Glossary.AND or root_instance == Glossary.OR):
            if root_instance.var == Glossary.AND:
                root_instance.var = Glossary.CONJUNCT
            else:
                root_instance.var = Glossary.DISJUNCT
            ops = root.get_ops()
            for n in ops:
                n.relation = Glossary.DUL_HAS_MEMBER

        if instance is None:
            return root

        if root.get_child(Glossary.AMR_CONCESSION) is not None:
            concession = root.get_child(Glossary.AMR_CONCESSION)
            condition = root.get_child(Glossary.AMR_CONDITION)
            swap = Node("", "")

            if (concession.get_instance() is not None and concession.get_instance().var == Glossary.EVEN_IF
                    and concession.get_child(Glossary.AMR_OP1) is not None):
                root.node_list.remove(concession)
                op1 = concession.get_child(Glossary.AMR_OP1)
                modality = Node(Glossary.BOXING_NECESSARY, Glossary.BOXING_HAS_MODALITY, Glossary.NodeStatus.OK)
                quality = Node(Glossary.FRED_EVEN, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK)
                root.add(modality)
                op1.add(modality)
                swap.substitute(root)
                root.substitute(op1)
                root.relation = swap.relation
                swap.relation = Glossary.FRED_ENTAILS
                swap.add(quality)
                root.add(swap)

            if (concession.get_instance() is not None and concession.get_instance().var == Glossary.EVEN_WHEN
                    and concession.get_child(Glossary.AMR_OP1) is not None):
                root.node_list.remove(concession)
                op1 = concession.get_child(Glossary.AMR_OP1)
                quality = Node(Glossary.FRED_EVEN, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK)
                op1.relation = Glossary.FRED_WHEN
                root.add(quality)
                root.add(op1)

            if condition is not None and condition.get_instance() is not None:
                root.node_list.remove(condition)
                modality = Node(Glossary.BOXING_NECESSARY, Glossary.BOXING_HAS_MODALITY, Glossary.NodeStatus.OK)
                root.add(modality)
                condition.add(modality)
                swap.substitute(root)
                root.substitute(condition)
                root.relation = swap.relation
                swap.relation = Glossary.FRED_ENTAILS
                root.add(swap)

        if instance.var == Glossary.SUM_OF or instance.var == Glossary.PRODUCT_OF:
            if instance.var == Glossary.SUM_OF:
                instance.var = Glossary.SUM
                for op in root.get_ops():
                    op.relation = Glossary.FRED + Glossary.SUM + Glossary.OF
            else:
                instance.var = Glossary.PRODUCT
                for op in root.get_ops():
                    op.relation = Glossary.FRED + Glossary.PRODUCT + Glossary.OF

        if instance.var == Glossary.AMR_RELATIVE_POSITION:
            if (root.get_child(Glossary.AMR_DIRECTION) is not None and root.get_child(Glossary.AMR_OP1) is not None
                    and root.get_child(Glossary.AMR_QUANT) is not None
                    and root.get_child(Glossary.AMR_QUANT).get_instance() is not None):
                op1 = self.get_original(root.get_child(Glossary.AMR_OP1))
                root.node_list.remove(op1)
                direction = self.get_original(root.get_child(Glossary.AMR_DIRECTION))
                op1.relation = Glossary.FRED + direction.get_instance().var + Glossary.OF
                direction.add(op1)
                quant = root.get_child(Glossary.AMR_QUANT)
                root.get_instance().var = quant.get_instance().var.replace(Glossary.QUANTITY, "")

        if len(instance.var) > 3 and re.match(Glossary.AMR_VERB, instance.var[-3:]) and not self.is_verb(
                instance.var) and len(root.get_args()) == 1:
            self.topic_flag = False
            arg = root.get_args()[0]
            root.node_list.remove(arg)
            if root.get_child(Glossary.AMR_DEGREE) is not None and root.get_child(
                    Glossary.AMR_DEGREE).get_instance() is not None:
                instance.var = root.get_child(
                    Glossary.AMR_DEGREE).get_instance().var.capitalize() + instance.var.capitalize()
                root.node_list.remove(root.get_child(Glossary.AMR_DEGREE))

            parent_id = root.get_node_id()
            arg_id = arg.get_node_id()
            parent_var = instance.var[0:-3]
            if arg.get_instance() is not None:
                instance.var = arg.get_instance().var
                self.remove_instance(arg)
            arg.make_equals(node_id=parent_id)
            arg.relation = Glossary.DUL_HAS_QUALITY
            arg.var = Glossary.FRED + parent_var.replace(Glossary.FRED, "")
            root.add_all(arg.node_list)
            arg.node_list = []
            root.add(arg)
            root.make_equals(node_id=arg_id)
            arg.set_status(Glossary.NodeStatus.OK)

        if (len(instance.var) > 3 and re.match(Glossary.AMR_VERB, instance.var[-3:])
                and not self.is_verb(instance.var, root.get_args())):
            if root.get_child(Glossary.AMR_ARG0) is not None and root.get_child(Glossary.AMR_ARG1) is not None:
                root.get_child(Glossary.AMR_ARG0).relation = Glossary.BOXER_AGENT
                root.get_child(Glossary.AMR_ARG1).relation = Glossary.BOXER_PATIENT
                self.topic_flag = False
            if root.get_child(Glossary.AMR_ARG1) is not None and root.get_child(Glossary.AMR_ARG2) is not None:
                root.get_child(Glossary.AMR_ARG1).relation = Glossary.VN_ROLE_EXPERIENCER
                root.get_child(Glossary.AMR_ARG2).relation = Glossary.VN_ROLE_CAUSE
                self.topic_flag = False

        if (root.get_child(Glossary.AMR_SCALE) is not None
                and root.get_child(Glossary.AMR_SCALE).get_instance() is not None):
            scale = root.get_child(Glossary.AMR_SCALE)
            scale.relation = Glossary.FRED_ON
            scale.var = scale.get_instance().var.capitalize() + Glossary.SCALE
            self.remove_instance(scale)

        if root.get_child(Glossary.AMR_ORD) is not None:
            ord_node = root.get_child(Glossary.AMR_ORD)
            root.node_list.remove(ord_node)
            self.remove_instance(ord_node)
            root.add_all(ord_node.node_list)
            value = ord_node.get_child(Glossary.AMR_VALUE)
            if value is not None and re.match(Glossary.NN_INTEGER, value.var):
                num = int(value.var)
                ord_num = self.ordinal(num)
                value.relation = Glossary.QUANT_HAS_QUANTIFIER
                value.var = Glossary.QUANT + ord_num

        return root

    def date_entity(self, root: Node) -> Node:
        """
        Elaborate on the date-related entities within the given root node.

        This method processes the root node, checking if it represents a date entity. If the root node
        is identified as a date entity, it then processes each of its child nodes related to date components
        (e.g., era, decade, century, calendar, weekday, etc.) by invoking the `date_child_elaboration` method.

        :param root: The root node to be processed and elaborated.
        :type root: Node
        :return: The modified root node after date entity elaboration.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        instance = root.get_instance()
        if len(root.node_list) == 0 or instance is None or instance.var != Glossary.AMR_DATE_ENTITY:
            return root
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_ERA))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_DECADE))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_CENTURY))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_CALENDAR))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_WEEKDAY))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_DAY_PERIOD))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_QUARTER))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_SEASON))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_TIMEZONE))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_YEAR))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_MONTH))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_DAY))
        self.date_child_elaboration(root.get_child(Glossary.AMR_DATE_YEAR2))
        return root

    def date_child_elaboration(self, child: Node):
        """
        Elaborate on a child node related to a date entity.

        This method modifies the given child node by updating its relation to reflect the AMRB prefix
        and applying any necessary transformations using `other_instance_elaboration_prefix`. The status
        of the child node is set to `NodeStatus.OK`.

        :param child: The child node to be processed.
        :type child: Node
        """
        if child is not None:
            child.relation = Glossary.AMRB + child.relation[1:]
            child = self.other_instance_elaboration_prefix(child, Glossary.AMRB)
            child.status = Glossary.NodeStatus.OK

    def prep_control(self, root: Node) -> Node:
        """
        Process a root node representing a preposition, adding a quality node and adjusting relations.

        This method checks if the root node represents a valid preposition and, if so, processes the
        node by creating a quality node, adjusting the relations of its child nodes, and handling any
        manner-related transformations. It updates the root node's relation and its node list accordingly.

        :param root: The root node to be processed.
        :type root: Node
        :return: The modified root node after preposition control elaboration.
        :rtype: Node
        """
        if len(root.node_list) == 0 or root.get_instance() is None or len(root.get_ops()) == 0:
            return root
        var = root.get_instance().var.replace(Glossary.FRED, "")
        quality = Node(Glossary.FRED + var.capitalize(), Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK)
        manner = root.get_child(Glossary.AMR_MANNER)
        if manner is not None:
            manner = manner.get_instance()
        go = False
        for prep in Glossary.PREPOSITION:
            if var == prep:
                go = True
                break
        if go:
            for node in root.get_ops():
                node.relation = root.relation
            if manner is not None and len(self.manner_adverb(manner.var)) > 0:
                quality.var = Glossary.FRED + self.manner_adverb(manner.var) + quality.var.capitalize()
                root.node_list.remove(root.get_child(Glossary.AMR_MANNER))
            else:
                quality.var = Glossary.FRED + quality.var.capitalize()
            root.add(quality)
            self.remove_instance(root)
            if root.relation == Glossary.TOP:
                root.relation = Glossary.PREP_SUBSTITUTION
            else:
                first = root.node_list[0]
                root.node_list.remove(first)
                first.add_all(root.node_list)
                root.substitute(first)
        return root

    @staticmethod
    def check_for_amr_instances(root: Node) -> bool:
        """
        Check if a root node has an AMR instance and a valid prefix.

        This method checks whether the root node has an instance from the list of defined AMR instances
        and if the node has a prefix. It returns `True` if both conditions are satisfied, otherwise returns `False`.

        :param root: The root node to be checked.
        :type root: Node
        :return: `True` if the node has a valid AMR instance with a prefix, `False` otherwise.
        :rtype: bool
        """
        if not isinstance(root, Node):
            return False
        instance = root.get_instance()
        if instance is None:
            return False
        for amr_instance in Glossary.AMR_INSTANCES:
            if instance.var == amr_instance and root.prefix:
                return True
        return False

    @staticmethod
    def manner_adverb(var: str) -> str:
        """
        Find a matching manner adverb for a given variable.

        This method searches through a list of defined manner adverbs and returns the first one that matches
        the given variable using regular expression matching. If no match is found, an empty string is returned.

        :param var: The variable to be checked for a matching manner adverb.
        :type var: str
        :return: The first matching manner adverb or an empty string if no match is found.
        :rtype: str
        """
        for adv in Glossary.MANNER_ADVERBS:
            if re.match("^" + var + ".*", adv):
                return adv
        return ""

    def other_instance_elaboration_prefix(self, root: Node, prefix: str) -> Node:
        """
        Elaborate on an instance by adding a prefix and handling special instances.

        This method updates the variable and relation of a node's instance based on a given prefix. It also
        handles special instances and modifies the relation to `RDF_TYPE` where applicable. The method ensures that
        the instance is updated with a unique variable and correct status.

        :param root: The root node to be processed.
        :type root: Node
        :param prefix: The prefix to be added to the instance's variable.
        :type prefix: str
        :return: The modified root node after elaboration.
        :rtype: Node
        """
        if not isinstance(root, Node):
            return root
        instance = root.get_instance()
        if instance is None:
            return root
        n_var = Glossary.FRED + instance.var + "_" + str(self.occurrence(instance.var))
        for node in self.get_equals(root):
            instance_in_list = node.get_instance()
            if instance_in_list is not None:
                node.var = n_var
                instance_in_list.relation = Glossary.RDF_TYPE
                flag = True
                if instance.var in Glossary.SPECIAL_INSTANCES:
                    instance_in_list.var = Glossary.SPECIAL_INSTANCES_PREFIX[
                                               Glossary.SPECIAL_INSTANCES.index(
                                                   instance.var)] + instance.var.capitalize()
                    flag = False
                if flag:
                    instance_in_list.var = prefix + instance.var.capitalize()
                if not instance_in_list.relation.startswith(Glossary.AMR_RELATION_BEGIN):
                    instance_in_list.set_status(Glossary.NodeStatus.OK)
            else:
                node.var = n_var
        return root

    def get_original(self, root: Node) -> Node | None:
        """
        Retrieve the original node matching the root node.

        This method searches for a node that matches the root node in terms of equality and ensures the node
        has a non-`None` instance. It returns the first matching node or `None` if no match is found.

        :param root: The root node to be checked for equality.
        :type root: Node
        :return: The original node matching the root node, or `None` if no match is found.
        :rtype: Node | None
        """
        if not isinstance(root, Node):
            return root
        for node in self.nodes:
            if root.__eq__(node) and node.get_instance() is not None:
                return node
        return None

    @staticmethod
    def ordinal(num: int) -> str:
        """
        Convert a number to its ordinal representation.

        This method converts a given integer into its corresponding ordinal form (e.g., 1 → "1st", 2 → "2nd",
        3 → "3rd", etc.). It handles exceptions for numbers 11, 12, and 13, which always have the "th" suffix.

        :param num: The integer to be converted into an ordinal.
        :type num: int
        :return: The ordinal representation of the given number.
        :rtype: str
        """
        suffixes = ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"]
        if num == 11 or num == 12 or num == 13:
            return str(num) + "th"
        else:
            return str(num) + suffixes[num % 10]

    @staticmethod
    def disambiguation(var: str) -> str:
        """
        Disambiguate a variable based on a predefined list of terms.

        This method checks if the given variable exists in the predefined list of DULs (`Glossary.DULS_CHECK`).
        If found, it returns the corresponding value from `Glossary.DULS`. Otherwise, it returns the variable
        prefixed with `Glossary.FRED`.

        :param var: The variable to be disambiguated.
        :type var: str
        :return: The disambiguated value or the original variable prefixed with `Glossary.FRED`.
        :rtype: str
        """
        for i, dul in enumerate(Glossary.DULS_CHECK):
            if dul == var.lower():
                return Glossary.DULS[i]
        return Glossary.FRED + var
