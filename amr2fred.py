import csv
import re
from glossary import Glossary
from unidecode import unidecode


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

    def increment_occurrence(self):
        self.__occurrence += 1


class Node:
    unique_id = 0
    level = 0

    def __init__(self, var, relation, status=Glossary.NodeStatus.AMR, visibility=True):
        self.relation = relation
        self.label = ""
        self.var = var
        self.node_list = []
        self.parent = None
        self.parent_list = []
        self.visibility = visibility
        self.prefix = False
        self.status = status
        self.node_type = Glossary.NodeType.OTHER
        self.__node_id = Node.unique_id
        Node.unique_id += 1
        self.verb = var
        self.malformed = False

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

    def to_string(self):
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
        for node in self.node_list:
            if node.relation == Glossary.INSTANCE:
                return node
        return None

    def get_child(self, relation):
        if isinstance(relation, str):
            for node in self.node_list:
                if node.relation == relation:
                    return node
        return None

    def get_inverse(self):
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
        nodes = []
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
            for n in self.node_list:
                new_node.add(n)
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
        snt = []
        for node in self.node_list:
            if node.relation == Glossary.AMR_SENTENCE:
                snt.append(node)
            snt += node.get_snt()
        return snt


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
        if Parser.__parser is None:
            Parser.__parser = Parser()
        return Parser.__parser

    def string2array(self, amr):
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
    def normalize(amr):
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
    def strip_accents(old):
        new = unidecode(old)
        return new

    def get_nodes(self, relation, amr_list):
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

    def check(self, root_node):
        if isinstance(root_node, Node):
            if root_node.status != Glossary.NodeStatus.OK:
                return None
            for i, node in enumerate(root_node.node_list):
                if node.status != Glossary.NodeStatus.OK:
                    self.removed.append(node)
                    root_node.node_list.pop(i)
                else:
                    root_node.node_list[i] = self.check(node)
            return root_node

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

    def fred_translate(self, root):
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

    def check_missing_instances(self, root):
        if isinstance(root, Node) and root.relation != Glossary.INSTANCE and root.get_instance() is None:
            for n in self.nodes:
                if n.var == root.var and n.get_instance() is not None:
                    root.make_equals(node=n)
        for i, node in enumerate(root.node_list):
            root.node_list[i] = self.check_missing_instances(node)
        return root

    def multi_sentence(self, root):
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

    def logic_triples_integration(self, root):
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

    def set_equals(self, root):
        return root

    def dom_verify(self, root):
        return root

    def control_ops(self, root):
        return root

    def li_verify(self, root):
        return root

    def inverse_checker(self, root):
        return root

    def mod_verify(self, root):
        return root

    def list_elaboration(self, root):
        return root

    def add_parent_list(self, root):
        return root

    def instance_elaboration(self, root):
        return root

    def verbs_elaboration(self, root):
        if not isinstance(root, Node):
            return None
        lemma = root.verb
        if root.node_type == Glossary.NodeType.VERB:
            pb = Propbank.get_propbank()
        return root

    def topic(self, root):
        if self.topic_flag:
            root.add(Node(Glossary.FRED_TOPIC, Glossary.DUL_HAS_QUALITY, Glossary.NodeStatus.OK))
        return root

    def residual(self, root):
        return root


if __name__ == '__main__':
    p = Parser.get_parser()
    nodo = p.parse('''(c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h 
    :location (p / public)) :op2 (r / resist-01 :ARG0 h :ARG1 (a2 / arrest-01 :ARG1 h))))''')

    print(nodo.to_string())
    # print(nodo)
    print(p.check(nodo))
