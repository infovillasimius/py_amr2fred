import csv
import re

from unidecode import unidecode

from glossary import Glossary


class Couple:
    def __init__(self, occurrence, word):
        self.__occurrence = occurrence
        self.__word = word

    def __str__(self):
        return "\nWord: " + self.__word + " - occurrences: " + self.__occurrence

    def get_word(self):
        return self.__word

    def get_occurrence(self):
        return self.__occurrence

    def set_occurrence(self, occurrence):
        self.__occurrence = occurrence

    def increment_occurrence(self):
        self.__occurrence += 1


class Node:
    unique_id = 0
    level = 0

    def __init__(self, var, relation, status=Glossary.NodeStatus.AMR, visibility=True):
        self.relation: str = relation
        self.label: str = ""
        self.var: str = var
        self.node_list: list = []
        self.parent: Node = None
        self.parent_list: list = []
        self.visibility: bool = visibility
        self.prefix: bool = False
        self.status: Glossary.NodeStatus = status
        self.node_type: Glossary.NodeType = Glossary.NodeType.OTHER
        self.__node_id: int = Node.unique_id
        Node.unique_id += 1
        self.verb: str = var
        self.malformed: bool = False

    def __str__(self):
        if Parser.endless > Glossary.ENDLESS:
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
        if Parser.endless > Glossary.ENDLESS:
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
        :rtype: Node
        """
        for node in self.node_list:
            if node.relation == Glossary.INSTANCE:
                return node
        return None

    def get_child(self, relation: str):
        """
        :rtype: Node
        """
        if isinstance(relation, str):
            for node in self.node_list:
                if node.relation == relation:
                    return node
        return None

    def get_inverse(self):
        """
        :rtype: Node
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

    def get_inverses(self):
        """
        :rtype: list[Node]
        """
        nodes: list[Node] = []
        for node in self.node_list:
            if (re.search(Glossary.AMR_INVERSE, node.relation) and
                    node.relation != Glossary.AMR_PREP_ON_BEHALF_OF and
                    node.relation != Glossary.AMR_CONSIST_OF and
                    node.relation != Glossary.AMR_PART_OF and
                    node.relation != Glossary.AMR_SUB_EVENT_OF and
                    node.relation != Glossary.AMR_QUANT_OF and
                    node.relation != Glossary.AMR_SUBSET_OF and
                    node.status != Glossary.NodeStatus.REMOVE):
                nodes.append(node)
        return nodes

    def make_equals(self, node=None, node_id=None):
        if node is not None:
            self.__node_id = node.__node_id
        elif node_id is not None:
            self.__node_id = node_id

    def add(self, node):
        self.node_list.append(node)
        node.parent = self

    def get_copy(self, node=None, relation=None, parser_nodes_copy=None):
        """
        :rtype: Node
        """
        if Parser.endless > Glossary.ENDLESS:
            return None

        if node is None and relation is None and parser_nodes_copy is None:
            Parser.endless += 1
            new_node = Node(self.var, self.relation, self.status)
            new_node.__node_id = self.__node_id
            for n in self.node_list:
                new_node.add(n.get_copy())
            return new_node

        if node is None and relation is not None and parser_nodes_copy is None:
            new_node = Node(self.var, relation, self.status)
            new_node.__node_id = self.__node_id
            return new_node

        if node is not None and relation is not None and parser_nodes_copy is None:
            new_node = Node(node.var, relation, node.status)
            new_node.__node_id = node.__node_id
            for n in node.node_list:
                new_node.add(n)
            return new_node

        if node is None and relation is None and parser_nodes_copy is not None:
            Parser.endless += 1
            new_node = Node(self.var, self.relation, self.status)
            new_node.__node_id = self.__node_id
            parser_nodes_copy.append(new_node)
            for n in self.node_list:
                new_node.add(n)
            return new_node

    def get_snt(self):
        """
        :rtype: list[Node]
        """
        snt = [Node]
        for node in self.node_list:
            if node.relation == Glossary.AMR_SENTENCE:
                snt.append(node)
            snt += node.get_snt()
        return snt

    def get_args(self):
        """
        :rtype: list[Node]
        """
        args_list = [Node]
        for node in self.node_list:
            if re.match(Glossary.AMR_ARG, node.relation.lower()):
                args_list.append(node)
        return args_list

    def get_node_id(self) -> int:
        return self.__node_id

    def get_nodes_with_parent_list_not_empty(self) -> list:
        snt = []
        for node in self.node_list:
            if len(node.parent_list) != 0:
                snt.append(node)
        return snt

    def get_children(self, relation):
        """
        :rtype: list[Node]
        """
        node_list = [Node]
        for node in self.node_list:
            if node.relation == relation:
                node_list.append(node)
        return node_list

    def add_all(self, node_list):
        if isinstance(node_list, list):
            self.node_list += node_list

    def set_status(self, status: Glossary.NodeStatus):
        self.status = status

    def get_ops(self):
        """
        :rtype: list[Node]
        """
        ops_list = []
        for node in self.node_list:
            if re.match(Glossary.AMR_OP, node.relation):
                ops_list.append(node)
        return ops_list


class Propbank:
    SEPARATOR = "\t"
    FILE1 = "propbankrolematrixaligned340.tsv"
    FILE2 = "propbankframematrix340.tsv"
    __propbank = None

    def __init__(self):
        self.role_matrix = self.file_read(Propbank.FILE1)
        self.frame_matrix = self.file_read(Propbank.FILE2)

    @staticmethod
    def get_propbank():
        """
        :rtype: Propbank
        """
        if Propbank.__propbank is None:
            Propbank.__propbank = Propbank()
        return Propbank.__propbank

    @staticmethod
    def file_read(file_name, delimiter="\t", encoding="utf8"):
        file = open(file_name, encoding=encoding)
        rate = csv.reader(file, delimiter=delimiter)
        header = []
        rows = []
        for i, row in enumerate(rate):
            if i == 0:
                header = row
            if i > 0:
                rows.append(row)
        return [header, rows]

    def frame_find(self, word, frame_field: Glossary.PropbankFrameFields) -> list:
        frame_list = []
        for frame in self.frame_matrix[1]:
            if word == frame[frame_field.value]:
                frame_list.append(frame)
        return frame_list

    def role_find(self, word, role_field, value, role_field_2) -> list:
        role_list = []
        for role in self.role_matrix[1]:
            if word == role[role_field.value] and value == role[role_field_2.value]:
                role_list.append(role)
        return role_list

    def list_find(self, word, args) -> list:
        result = []
        num = len(args)
        cfr = 0
        if Glossary.PB_ROLESET not in word:
            word = Glossary.PB_ROLESET + word
        node_list = self.frame_find(word, Glossary.PropbankRoleFields.PB_Frame)
        for node in args:
            assert isinstance(node, Node)
            r = Glossary.PB_SCHEMA + node.relation[1:]
            for l1 in node_list:
                if l1[Glossary.PropbankRoleFields.PB_ARG.value] == r:
                    cfr += 1
                    result += self.role_find(r, Glossary.PropbankRoleFields.PB_ARG, word,
                                             Glossary.PropbankRoleFields.PB_Frame)
                    break
        if cfr >= num:
            return result
        return None


class Parser:
    __parser = None
    endless = 0
    endless2 = 0

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
        :rtype: Parser
        """
        if Parser.__parser is None:
            Parser.__parser = Parser()
        return Parser.__parser

    def string2array(self, amr: str) -> list[str]:
        word_list = []
        amr = self.normalize(amr)
        # word_list_2 = [x if Glossary.QUOTE not in x else Glossary.LITERAL + x.replace(Glossary.QUOTE, "") for x in
        #                amr.strip().split(" ")]
        # print(word_list_2)
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
            print(e)
            return None

        return word_list

    @staticmethod
    def normalize(amr: str) -> str:
        re.sub("\r\n|\r|\n", " ", amr)
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
        return unidecode(amr)

    def get_nodes(self, relation, amr_list) -> Node:
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
                        print(e)
                        new_node = Node(amr_list[i + 1], word)
                        root.add(new_node)
                        self.nodes.append(new_node)
            i += 1
        if liv != 0:
            return None
        return root

    def check(self, root: Node) -> Node:
        if isinstance(root, Node):
            if root.status != Glossary.NodeStatus.OK:
                return None
            for i, node in enumerate(root.node_list):
                if node.status != Glossary.NodeStatus.OK:
                    self.removed.append(node)
                    root.node_list.pop(i)
                else:
                    root.node_list[i] = self.check(node)
        return root

    def parse(self, amr):
        amr = self.strip_accents(amr)
        root = self.get_nodes(Glossary.TOP, self.string2array(amr))

        if root is not None:
            Parser.endless = 0
            Parser.endless2 = 0
            self.root_copy = root.get_copy(parser_nodes_copy=self.nodes_copy)
            if Parser.endless > Glossary.ENDLESS:
                self.root_copy = Node("Error", "Recursive")
                return root

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
        if not isinstance(root, Node):
            return None
        elif len(root.node_list) == 0:
            self.set_equals(root)  # verificare comportamento
            return root

        if Parser.endless > Glossary.ENDLESS:
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
        if isinstance(root, Node) and root.relation != Glossary.INSTANCE and root.get_instance() is None:
            for n in self.nodes:
                if n.var == root.var and n.get_instance() is not None:
                    root.make_equals(node=n)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.check_missing_instances(node)
        return root

    def multi_sentence(self, root: Node) -> Node:
        if (isinstance(root, Node) and root.get_instance() is not None
                and root.get_instance().var == Glossary.AMR_MULTI_SENTENCE):
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
        for node in self.get_equals(root):
            node.var = root.var

    def get_equals(self, root: Node) -> list[Node]:
        return [node for node in self.nodes if node.__eq__(root)]

    def dom_verify(self, root: Node) -> Node:
        dom = root.get_child(Glossary.AMR_DOMAIN)
        if dom is not None:
            instance = root.get_instance()
            if instance is None:
                instance = self.get_instance(root.get_node_id())
            self.topic_flag = False
            dom.relation = Glossary.TOP
            if dom.get_instance() is None and self.get_instance(dom.get_node_id()) is not None:
                n_var = self.get_instance(dom.get_node_id())
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
        if isinstance(root, Node) and root.relation == Glossary.AMR_LI:
            root.relation = Glossary.TOP
            var = root.parent.var
            new_instance = Node(Glossary.REIFI_HAVE_LI, Glossary.INSTANCE)
            self.nodes.append(new_instance)
            arg1 = Node(root.var, Glossary.AMR_ARG1)
            self.nodes.append(arg1)
            arg2 = Node(var, Glossary.AMR_ARG2)
            self.nodes.append(arg2)
            arg2.make_equals(root.parent)
            root.var = "li_" + root.get_node_id()
            root.add(new_instance)
            root.add(arg1)
            root.add(arg2)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.li_verify(node)
        return root

    def inverse_checker(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root

        inv_nodes = root.get_inverses()

        if len(inv_nodes) == 0:
            return root

        if root.relation == Glossary.TOP and len(inv_nodes) == 1 and root.get_node_id() == 0:
            print(inv_nodes[0] is None)
            n = root.get_inverse()
            root.node_list.remove(n)
            root.relation = n.relation[0:-3]
            n.add(root)
            n.relation = Glossary.TOP
            return self.inverse_checker(n)
        else:
            for node in inv_nodes:
                new_node = root.get_copy(node.relation[0:-3])
                self.nodes.append(new_node)
                node.relation = Glossary.TOP
                node.add(new_node)

        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.inverse_checker(node)

        return root

    def mod_verify(self, root: Node) -> Node:
        if not isinstance(root, Node):
            return root
        flag = True
        instance = self.get_instance(root.get_node_id())
        if isinstance(instance, Node) and len(instance.var) > 3 and re.fullmatch(Glossary.AMR_VERB, instance.var[3:]):
            flag = False

        dom = root.get_child(Glossary.AMR_DOMAIN)
        mods = root.get_children(Glossary.AMR_MOD)

        for mod_node in mods:
            if isinstance(mod_node, Node) and flag:
                if isinstance(mod_node.get_instance(), Node):
                    mod_instance = mod_node.get_instance()
                elif isinstance(self.get_instance(mod_node.get_node_id()), Node):
                    mod_instance = self.get_instance(mod_node.get_node_id())
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
                        mod_ins = self.get_instance(mod_node.get_node_id()).var
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
                            root.var = Glossary.FRED + root_ins.lower() + "_" + self.occurrence(root_ins)
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
                pass
                if mod_node.get_instance() is not None:
                    mod_ins = mod_node.get_instance().var
                else:
                    mod_ins = self.get_instance(mod_node.get_node_id()).var
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
        # TODO
        return root

    def add_parent_list(self, root: Node) -> Node:
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
        if not isinstance(root, Node):
            return None
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
                                                Glossary.PB_SCHEMA + node.relation[1:],
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
        if self.topic_flag:
            root.add(Node(Glossary.FRED_TOPIC, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK))
        return root

    def residual(self, root: Node) -> Node:
        # TODO
        return root

    def get_instance(self, node_id) -> Node:
        for node in self.nodes_copy:
            if node.get_node_id() == node_id and node.get_instance() is not None:
                return node.get_instance()
        return None

    def treat_instance(self, root: Node):
        for node in self.get_equals(root):
            node.var = root.var
        if root.get_instance() is not None:
            root.get_instance().status = Glossary.NodeStatus.REMOVE

    def remove_instance(self, root: Node):
        for node in self.get_equals(root):
            node.var = root.var
        if root.get_instance() is not None:
            root.node_list.remove(root.get_instance())

    @staticmethod
    def is_verb(var, node_list=None) -> bool:
        prb = Propbank.get_propbank()
        if node_list is None and isinstance(var, str):
            result = prb.frame_find(Glossary.PB_ROLESET + var, Glossary.PropbankFrameFields.PB_Frame)
            return result is not None and len(result) > 0
        elif isinstance(var, str) and isinstance(node_list, list):
            result = prb.list_find(var, node_list)
            return result is not None and len(result) > 0

    def occurrence(self, word) -> int:
        occurrence_num = 1
        for couple in self.couples:
            if word == couple.get_word():
                occurrence_num += couple.get_occurrence()
                couple.set_occurrence(occurrence_num)
        if occurrence_num == 1:
            self.couples.append(Couple(1, word))
        return occurrence_num

    def args(self, root: Node):
        # TODO
        pass

    def other_instance_elaboration(self, root: Node) -> Node:
        # TODO
        return root


if __name__ == '__main__':
    p = Parser.get_parser()
    nodo = p.parse('''(c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h
    :location (p / public)) :op2 (r / resist-01 :ARG0 h :ARG1 (a2 / arrest-01 :ARG1 h))))''')
    # nodo = p.parse("(z0 / lawyer :domain (z1 / man))")
    print(nodo.to_string())
    # print(nodo)
    # print(p.check(nodo))
