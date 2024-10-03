# py_amr2fred

From Abstract Meaning Representation [AMR](https://amr.isi.edu/) to RDF, according
to [FRED](http://wit.istc.cnr.it/stlab-tools/fred/)'s formal semantics and ontology design patterns.

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


## Parameter [amr]:

amr string in penman format


## Parameter [serialize]:

- [True] returns a string
- [False] returns a rdflib Graph


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

- [True] the library will use alt. API
- [False] the library will use default API

## Parameter [multilingual]

- [True] the library will use multilingual API
- [False] the library will use "English only" API

## Parameter [graphic]

- [svg] return a svg string
- [png] returns a png tmp_file

## !!Attention!!

- In order to generate graphical output (such as PNG or SVG files), you must have Graphviz installed on your system. You
  can download and install it from [Graphviz's Official Website](https://graphviz.org/). If Graphviz is not installed,
  the library will return a String containing the graph translated into the .dot graphic language instead of generating
  the PNG or SVG graphical output.

- When a PNG file is generated, the temporary file will not be automatically deleted. You need to manually manage or
  delete the file after using it.

