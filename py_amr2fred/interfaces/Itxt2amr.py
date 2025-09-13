from typing import Optional
import logging
from abc import ABC, abstractmethod

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class IText2AMR(ABC):

    @abstractmethod
    def __init__(self,
            *args,
            **kwargs
        ):
        """
            Retrieves the AMR representation of the given text using the appropriate API.
        """
        pass

    @abstractmethod
    def get_amr(self,
            text: str,
            *args,
            **kwargs
        ) -> Optional[str]:
        """
            Retrieves the AMR representation of the given text using the appropriate API.
            :param text: Input text to convert into AMR.
            :return: The AMR representation as a string.
        """
        pass
