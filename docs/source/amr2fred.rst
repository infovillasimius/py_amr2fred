amr2fred module
===============

.. automodule:: .amr2fred
   :members:
   :show-inheritance:
   :undoc-members:


Amr2fred class parameters
-------------------------

**txt2amr_uri**
    Specifies the API URI of an alternative Spring-based "txt2amr" translator. This parameter is optional and only required
    if users wish to override the default resource. It should be used in conjunction with the **alt_api** parameter of
    the **translate** method.

**m_txt2amr_uri**
    Specifies the API URI of an alternative multilingual USeA-based "txt2amr" translator. This parameter is optional and
    only required if users wish to override the default multilingual resource. It should be used in conjunction with
    the **multilingual** parameter of the **translate** method.

translate method parameters
---------------------------

**amr**
    AMR string in Penman format.

**serialize**
    - **True** returns a string.
    - **False** returns an rdflib Graph.

**mode**
    - Glossary.RdflibMode.TURTLE
    - Glossary.RdflibMode.NT
    - Glossary.RdflibMode.XML
    - Glossary.RdflibMode.N3
    - Glossary.RdflibMode.JSON_LD

**alt_fred_ns**
    Alternate URI for base Fred namespace.

**text**
    Natural Language text to translate.

**alt_api**
    - **True**: The library will use the alternative API.
    - **False**: The library will use the default API (default).

**multilingual**
    - **True**: The library will use the multilingual API.
    - **False**: The library will use the "English only" API (default).

**graphic**
    - **svg**: Returns an SVG string.
    - **png**: Returns a PNG temporary file.

**post_processing**
    - **True**: Perform WSD and KG enrichment (default).
    - **False**: Do not perform WSD and KG enrichment.

    The post-processing feature requires a database file for mapping Wikipedia IDs to WikiData IDs. The system will automatically download the required file (`index_enwiki-latest.db`, ~1815 MB uncompressed, ~832 MB compressed) during its first run. Ensure you have sufficient disk space and a stable internet connection before running the system for the first time.

get_amr method parameters
-------------------------

**text**
    Input text to convert into AMR.

**alt_api**
    - **True**: Uses the predefined alternative API or a custom one provided during class instantiation.
    - **False**: Uses the default API.

**multilingual**
    - **True**: Uses the multilingual text-to-AMR service.
    - **False**: Uses the default English-only text-to-AMR service.

!! Attention !!
---------------

- In order to generate graphical output (such as PNG or SVG files), you must have Graphviz installed on your system. You can download and install it from `Graphviz's Official Website <https://graphviz.org/>`_. If Graphviz is not installed, the library will return a String containing the graph translated into the .dot graphic language instead of generating the PNG or SVG graphical output.

- When a PNG file is generated, the temporary file will not be automatically deleted. You need to manually manage or delete the file after using it.
