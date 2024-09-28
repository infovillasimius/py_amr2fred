# py_amr2fred

From Abstract Meaning Representation AMR (https://amr.isi.edu/) to RDF, according to the syntax of
FRED (http://wit.istc.cnr.it/stlab-tools/fred/)

Python version of
[amr2fred](http://framester.istc.cnr.it/amr-2-fred)'s core functions

Install:

```
pip install py_amr2fred
```

## Use:

```
from py_amr2fred import *
amr2fred = Amr2fred()
mode = Glossary.RdflibMode.N3
amr_text = """
    (c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h 
	:location (p / public)) :op2 (r / resist-01 :ARG0 h 
	:ARG1 (a2 / arrest-01 :ARG1 h))))
"""
# translate from AMR
print(amr2fred.translate(amr_text, serialize=True, mode=mode, alt_fred_ns=None))

# translate from natural language
print(amr2fred.translate(text="Four boys making pies", serialize=True, alt_api=False
      mode=Glossary.RdflibMode.TURTLE, alt_fred_ns="http://fred-01/domain.owl#"))
```


## Parameter [amr]:

amr string in penman format


## Parameter [serialize]:

[True] returns a string

[False] returns a rdflib Graph


## Parameter [mode]:

- Glossary.RdflibMode.TURTLE
- Glossary.RdflibMode.NT
- Glossary.RdflibMode.XML
- Glossary.RdflibMode.N3
- Glossary.RdflibMode.JSON_LD



## Parameter [alt_fred_ns]: 

Alternate Uri for base Fred NS


## Parameter [text]

NL text to translate 


## Parameter [alt_api]

[True] the library will use alt. API

[False] the library will use default API

## Parameter [multilingual]

[True] the library will use multilingual API

[False] the library will use "English only" API

