import csv
import os

from .glossary import Glossary
from .node import Node


class Propbank:
    """
    A class to represent Propbank data, which includes role and frame matrices.

    This class provides methods to read Propbank data from TSV files,
    search for frames and roles, and find specific relationships between words.

    """

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
        Returns the singleton instance of the Propbank class.

        If the instance does not exist, it will create a new one.

        :rtype: Propbank
        """
        if Propbank.__propbank is None:
            Propbank.__propbank = Propbank()
        return Propbank.__propbank

    @staticmethod
    def file_read(file_name: str, delimiter: str = "\t", encoding: str = "utf8") -> list:
        """
        Reads a TSV file and returns its header and rows.

        The file is read using the specified delimiter and encoding, and the
        first row is treated as the header. The function returns a list with
        the header and the remaining rows.

        :param file_name: Path to the file to read.
        :type file_name: str
        :param delimiter: The delimiter used to separate columns in the file.
        :type delimiter: str
        :param encoding: The encoding to use when reading the file.
        :type encoding: str
        :return: A list containing the header and rows of the file.
        :rtype: list
        """
        file = open(file_name, encoding=encoding)
        rate = csv.reader(file, delimiter=delimiter)
        header = []
        rows = []
        for i, row in enumerate(rate):
            if i == 0:
                header = row
            if i > 0:
                rows.append(row)
        file.close()
        return [header, rows]

    def frame_find(self, word: str, frame_field: Glossary.PropbankFrameFields) -> list:
        """
        Finds frames that match a given word in a specified frame field.

        The method searches through the frame matrix and returns a list of frames
        where the specified field contains the word.

        :param word: The word to search for in the frame matrix.
        :type word: str
        :param frame_field: The field to search for the word in the frame.
        :type frame_field: Glossary.PropbankFrameFields
        :return: A list of frames that match the given word in the specified field.
        :rtype: list
        """
        frame_list = []
        for frame in self.frame_matrix[1]:
            if word.casefold() == frame[frame_field.value].casefold():
                frame_list.append(frame)
        # print(frame_list)
        return frame_list

    def role_find(self, word: str,
                  role_field: Glossary.PropbankRoleFields,
                  value: str,
                  role_field_2: Glossary.PropbankRoleFields) -> list:
        """
        Finds roles matching a given word and values in specific fields.

        This method searches through the role matrix and returns a list of roles
        that match the provided word, value, and fields.

        :param word: The word to search for in the role matrix.
        :type word: str
        :param role_field: The field in the role matrix to match the word.
        :type role_field: Glossary.PropbankRoleFields
        :param value: The value to match in the second role field.
        :type value: str
        :param role_field_2: The second role field to compare the value.
        :type role_field_2: Glossary.PropbankRoleFields
        :return: A list of roles that match the given word and values.
        :rtype: list
        """
        role_list = []
        for role in self.role_matrix[1]:
            if (word.casefold() == role[role_field.value].casefold()
                    and value.casefold() == role[role_field_2.value].casefold()):
                role_list.append(role)
        return role_list

    def list_find(self, word: str, args: list[Node]) -> list | None:
        """
        Finds roles and relationships for a word based on a list of `Node` objects.

        The method iterates over a list of `Node` objects and searches for roles
        that match the word using the `role_find` method. It returns a list of
        results if enough matches are found.

        :param word: The word to search for in the role matrix.
        :type word: str
        :param args: A list of `Node` objects to find roles for.
        :type args: list[Node]
        :return: A list of roles if enough matches are found, or None.
        :rtype: list | None
        """
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
