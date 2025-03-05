Installation
============

`py_amr2fred` is a Python library that transforms natural language text into RDF/OWL Knowledge Graphs
through Abstract Meaning Representation (AMR).

Requirements
------------

- **Python 3.11+** is required.
- The following dependencies will be installed automatically via `pip`:

  - `Unidecode~=1.3.8`
  - `requests~=2.32.3`
  - `nltk~=3.9.1`
  - `rdflib~=7.1.1`
  - `SPARQLWrapper~=2.0.0`
  - `wikimapper~=0.2.0`
  - `tqdm~=4.67.1`

Installation via pip
--------------------

To install the latest version, run:

.. code-block:: bash

    pip install py_amr2fred

If you choose to clone the `repository <https://github.com/infovillasimius/py_amr2fred>`_, you can ensure all dependencies are installed by running:

.. code-block:: bash

    pip install -r requirements.txt

where `requirements.txt` should contain:

.. code-block:: text

    Unidecode~=1.3.8
    requests~=2.32.3
    nltk~=3.9.1
    rdflib~=7.1.1
    SPARQLWrapper~=2.0.0
    wikimapper~=0.2.0
    tqdm~=4.67.1

You can find the repository here: `<https://github.com/infovillasimius/py_amr2fred>`_

Graphical Output (Optional)
---------------------------

To generate graphical outputs (such as PNG or SVG files), you must have **Graphviz** installed on your system.
If Graphviz is not installed, the library will return a string containing the graph in the `.dot` format
instead of generating graphical outputs.

You can download and install Graphviz from:

- `Graphviz Official Website <https://graphviz.org/>`_


