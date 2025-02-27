import csv
import os

from glossary import Glossary
from node import Node


class Propbank:
    current_directory = os.path.dirname(__file__)
    SEPARATOR = "\t"
    FILE1 = os.path.join(current_directory, "propbankrolematrixaligned340.tsv")
    FILE2 = os.path.join(current_directory, "propbankframematrix340.tsv")
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
            if word.casefold() == frame[frame_field.value].casefold():
                frame_list.append(frame)
        return frame_list

    def role_find(self, word, role_field, value, role_field_2) -> list:
        role_list = []
        for role in self.role_matrix[1]:
            if (word.casefold() == role[role_field.value].casefold()
                    and value.casefold() == role[role_field_2.value].casefold()):
                role_list.append(role)
        return role_list

    def list_find(self, word, args: list[Node]) -> list[Node] | None:
        result = []
        num = len(args)
        cfr = 0
        if Glossary.PB_ROLESET not in word:
            word = Glossary.PB_ROLESET + word
        for node in args:
            r = Glossary.PB_SCHEMA + node.relation[1:]
            res = self.role_find(r, Glossary.PropbankRoleFields.PB_ARG, word, Glossary.PropbankRoleFields.PB_Frame)
            if len(res) > 0:
                result.append(res[0])
                cfr += 1
        if cfr >= num:
            return result
        return None
