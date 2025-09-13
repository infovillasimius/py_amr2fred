from typing import Optional
import json
import logging
import urllib.parse
import requests

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .interfaces.Itxt2amr import IText2AMR

class Text2AMR(IText2AMR):

    def __init__(self,
            txt2amr_uri: Optional[str] = None,
            m_txt2amr_uri: Optional[str] = None
        ):
        """
            Retrieves the AMR representation of the given text using the appropriate API.
        """
        self.spring_uri = "https://arco.istc.cnr.it/spring/text-to-amr?blinkify=true&sentence="
        
        self.spring_uni_uri = ("https://nlp.uniroma1.it/spring/api/text-to-amr?sentence="
                               if txt2amr_uri is None else txt2amr_uri)
        self.usea_uri = ("https://arco.istc.cnr.it/usea/api/amr" if m_txt2amr_uri is None else m_txt2amr_uri)
    

    def get_amr(self,
            text: str,
            alt_api: bool,
            multilingual: bool
        ) -> Optional[str]:
        """
            Retrieves the AMR representation of the given text using the appropriate API.
            :param text: Input text to convert into AMR.
            :param alt_api: Whether to use the predefined alternative API or a custom one provided during class instantiation.
            :param multilingual: Whether to use the multilingual text-to-AMR service.
            :return: The AMR representation as a string.
        """
        try:
            if multilingual:
                uri = self.usea_uri
                post_request = {
                    "sentence": {
                        "text": text
                    }
                }
                amr = json.loads(requests.post(uri, json=post_request).text).get("amr_graph")
            else:
                if alt_api:
                    uri = self.spring_uni_uri + urllib.parse.quote_plus(text)
                else:
                    uri = self.spring_uri + urllib.parse.quote_plus(text)
                amr = json.loads(requests.get(uri).text).get("penman")
            return amr
        except Exception as e:
            logger.warning(str(e))
            return None
