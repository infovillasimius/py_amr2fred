# py_amr2fred

From Text to Abstract Meaning Representation to RDF/OWL Knowledge Graph

Python library version of
[Text2AMR2FRED](https://arco.istc.cnr.it/txt-amr-fred/) incorporating the core functions of
[amr2fred](http://framester.istc.cnr.it/amr-2-fred).
It enables seamless transformation of natural language text into RDF/OWL Knowledge Graphs
through Abstract Meaning Representation ([AMR](https://amr.isi.edu/)), according
to [FRED](http://wit.istc.cnr.it/stlab-tools/fred/)'s formal semantics and ontology design patterns.


Install:

```
pip install py_amr2fred
```

## Use:

```
import os
from pathlib import Path
from py_amr2fred import *
amr2fred = Amr2fred()
mode = Glossary.RdflibMode.N3
amr_text = """
    (c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h 
	:location (p / public)) :op2 (r / resist-01 :ARG0 h 
	:ARG1 (a2 / arrest-01 :ARG1 h))))
"""
# translate from AMR
print(amr2fred.translate(amr_text, serialize=True, mode=mode))

# translate from natural language
mode = Glossary.RdflibMode.TURTLE
print(amr2fred.translate(text="Four boys making pies", serialize=True, mode=mode))

# multilingual
print(amr2fred.translate(text="Quattro ragazzi preparano torte", 
                         serialize=True, 
                         mode=Glossary.RdflibMode.TURTLE,  
                         multilingual=True))

# PNG image output !!Attention!! Graphviz must be installed! The temporary file will not be automatically deleted
png_file = amr2fred.translate(text="Four boys making pies", graphic="png")

save_path = "output_image.png"
with open(save_path, 'wb') as f:
    f.write(png_file.read())
png_file.close()
os.remove(Path(png_file.name))

# SVG image output !!Attention!! Graphviz must be installed!
svg = amr2fred.translate(text="Four boys making pies", graphic="svg")

save_path = "output_image.svg"
with open(save_path, 'w') as f:
    f.write(svg)      
```

## Amr2fred class parameters:

### Parameter [txt2amr_uri]

Specifies the API URI of an alternative Spring-based "txt2amr" translator. This parameter is optional and only required
if users wish to override the default resource. It should be used in conjunction with the [alt_api] parameter of
the [translate] method.

### Parameter [m_txt2amr_uri]

Specifies the API URI of an alternative multilingual USeA-based "txt2amr" translator. This parameter is optional and
only required if users wish to override the default multilingual resource. It should be used in conjunction with
the [multilingual] parameter of the [translate] method.

## [translate] method parameters:

### Parameter [amr]:

amr string in penman format

### Parameter [serialize]:

- [True] returns a string
- [False] returns a rdflib Graph

### Parameter [mode]:

- Glossary.RdflibMode.TURTLE
- Glossary.RdflibMode.NT
- Glossary.RdflibMode.XML
- Glossary.RdflibMode.N3
- Glossary.RdflibMode.JSON_LD

### Parameter [alt_fred_ns]:

Alternate Uri for base Fred NS

### Parameter [text]

NL text to translate 

### Parameter [alt_api]

- [True] the library will use alt. API
- [False] the library will use default API (default)

### Parameter [multilingual]

- [True] the library will use multilingual API
- [False] the library will use "English only" API (default)

### Parameter [graphic]

- [svg] return a svg string
- [png] returns a png tmp_file

### Parameter [post_processing]

- [True] perform WSD and KG enrichment (default)
- [False] do not perform WSD and KG enrichment

The post-processing feature requires a database file for mapping Wikipedia IDs to WikiData IDs. The system will
automatically download the required file (`index_enwiki-latest.db`, ~1815 MB uncompressed, ~832 MB compressed) during
its first run. Ensure you have sufficient disk space and a stable internet connection before running the system for the
first time.

## !!Attention!!

- In order to generate graphical output (such as PNG or SVG files), you must have Graphviz installed on your system. You
  can download and install it from [Graphviz's Official Website](https://graphviz.org/). If Graphviz is not installed,
  the library will return a String containing the graph translated into the .dot graphic language instead of generating
  the PNG or SVG graphical output.

- When a PNG file is generated, the temporary file will not be automatically deleted. You need to manually manage or
  delete the file after using it.

![Read the Docs Badge](https://img.shields.io/badge/docs-read%20the%20docs-blue)

For full documentation, visit: [Read the Docs](https://py-amr2fred.readthedocs.io/)
