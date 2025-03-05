Usage
=====

Once installed, you can use `py_amr2fred` to translate natural language text or AMR structures into RDF/OWL Knowledge Graphs.

Basic Example
-------------

.. code-block:: python

    from py_amr2fred import Amr2fred, Glossary

    amr2fred = Amr2fred()
    mode = Glossary.RdflibMode.N3
    amr_text = """
        (c / charge-05 :ARG1 (h / he) :ARG2 (a / and
            :op1 (i / intoxicate-01 :ARG1 h :location (p / public))
            :op2 (r / resist-01 :ARG0 h :ARG1 (a2 / arrest-01 :ARG1 h))))
    """

    # Translate from AMR
    print(amr2fred.translate(amr_text, serialize=True, mode=mode))

    # Translate from natural language
    print(amr2fred.translate(text="Four boys making pies", serialize=True, mode=Glossary.RdflibMode.TURTLE))

Multilingual Translation
------------------------

.. code-block:: python

    print(amr2fred.translate(text="Quattro ragazzi preparano torte",
                             serialize=True,
                             mode=Glossary.RdflibMode.TURTLE,
                             multilingual=True))

Graphical Output
----------------

To generate images (requires Graphviz):

.. code-block:: python

    png_file = amr2fred.translate(text="Four boys making pies", graphic="png")

    with open("output_image.png", 'wb') as f:
        f.write(png_file.read())

    png_file.close()
    os.remove(Path(png_file.name))

**Note:** When generating PNG files, temporary files will not be automatically deleted. You must manage or remove them manually.

.. warning::
   Ensure Graphviz is installed to generate graphical outputs.

For SVG output:

.. code-block:: python

    svg = amr2fred.translate(text="Four boys making pies", graphic="svg")

    with open("output_image.svg", 'w') as f:
        f.write(svg)

More Details
------------

For advanced usage, including API customization and translation options, refer to the full documentation on :doc:`amr2fred`..
