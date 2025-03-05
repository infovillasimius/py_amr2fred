class Couple:
    """
    A class representing a pair of a word and its occurrence count.

    The `Couple` class stores a word and its associated occurrence count.
    It provides methods to retrieve the word, the count, update the count,
    and increment the occurrence count.

    :param occurrence: The initial occurrence count of the word.
    :param word: The word associated with the occurrence count.
    """
    def __init__(self, occurrence, word):
        self.__occurrence = occurrence
        self.__word = word

    def __str__(self):
        return "\nWord: " + self.__word + " - occurrences: " + str(self.__occurrence)

    def get_word(self) -> str:
        """
        Returns the word associated with the Couple instance.

        :return: The word.
        :rtype: str
        """
        return self.__word

    def get_occurrence(self) -> int:
        """
        Returns the occurrence count of the word.

        :return: The occurrence count.
        :rtype: int
        """
        return self.__occurrence

    def set_occurrence(self, occurrence):
        """
        Sets the occurrence count for the word.

        :param occurrence: The new occurrence count to set.
        """
        self.__occurrence = occurrence

    def increment_occurrence(self):
        """
        Increments the occurrence count by 1.
        """
        self.__occurrence += 1
