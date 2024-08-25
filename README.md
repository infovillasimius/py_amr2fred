# py_amr2fred

From Abstract Meaning Representation AMR (https://amr.isi.edu/) to RDF, according to the syntax of
FRED (http://wit.istc.cnr.it/stlab-tools/fred/)

Python version of
[amr2fred](http://framester.istc.cnr.it/amr-2-fred)'s core functions

Install:

```
pip install py_amr2fred
```

Use:

```
from py_amr2fred import *
amr2fred = Amr2fred()
mode = Glossary.Rdflib_mode.N3
amr_text = """
    (c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h :location (p / public)) 
    :op2 (r / resist-01 :ARG0 h :ARG1 (a2 / arrest-01 :ARG1 h))))
"""
print(amr2fred.translate(amr_text, serialize=True, mode=mode))
```

serialize=True returns a string

serialize=False returns a rdflib Graph

Possible formats:

- Glossary.Rdflib_mode.TURTLE
- Glossary.Rdflib_mode.NT
- Glossary.Rdflib_mode.XML
- Glossary.Rdflib_mode.N3
- Glossary.Rdflib_mode.JSON_LD


