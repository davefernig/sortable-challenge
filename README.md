# Sortable Coding Challenge
This is my entry to the Sortable Coding Challenge. It is essentially a hashing solution. If there are constant bounds on the number of manufacturers, families per manufacturer, and the character-length of listing titles, it runs in linear time. On my machine (1.7GHz) it takes about 3s.

## Requires
Python 2

## Usage

Clone the repository, navigate to src, and run parse.py: 
```
cd sortable-challenge/src/
python parse.py
```
The output will be written to sortable-challenge/output/results.json. To visually examine the results (one product at a time), use:
```
python inspect.py results.json
```

To visually compare the differences between the output of different versions (analogous to the command line tool diff), use:
```
python compare.py results_v1.json results_v2.json
```

##Implementation Details

### Cleaning
- Some rule-based substitutions are made (the Greek letter mu becomes 'mju', 'hewlett packard' is replaced with 'hp', etc). There are opportunities for further gains here, I have only implemented ones that seemed to yield obvious performance gains based on visually examining the output. 
- Strings are sent to lower, split into their alphabetic and numeric components, and other chars removed (e.g. so that "XL-200s" is equivalent to "xl 200 s") 

### Data Structures
The items in products.txt are hashed into a tree (implemented as a nested dict) with a hierarchichal structure:

Manufacturer (frozenset)   
&nbsp;  &nbsp; &nbsp; &nbsp; |  
&nbsp;  &nbsp; &nbsp; &nbsp; | ---- Family  (tuple(str))   
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |   
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | ---- Model (tuple(str))  
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |      
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | ---- Results (list)  

### Algorithm
The file listings.txt is read, each listing is parsed, and an attempt is made to match the manufacturer, family, and model.

- To match against manufacturers, first look at the set intersections of the manufacturer field with each manufacturer in the tree. If we get exactly one hit we take that to be the manufacturer. If we don't get a hit, we try with the description, but then we add some additional checks because this is often indicative of an accessory. If we get multiple hits we skip the listing.

- Assuming we have hit on exactly one manufacturer, we try to match against that manufacturer's product families. We do this by checking every n-gram in the title, where n runs through the number of strings. Here we allow for multiple hits.

- Finally, we try to match on a specific model, in a similar fashion to matching on families. If we get exactly one hit, we add the listing to that branch. Each token can only contribute to one model – if there are overlapping model codes we take the longest. 

## Assumptions
I made following assumptions:

1. For each product, we want to recall every listing whose contents are a superset of that product (and no other product).  
E.g. A listing for a Pentax K-7 and an extra lens will be matched against Pentax K-7.  
E.g. A listing for a Pentax K-7 and a Sony Alpha NEX-5A will not be matched against anything.  
E.g. A listing for a Pentax K-7 accessory kit (no camera) will not be matched against anything.

2. We want to recall all variants of a given product (e.g. A listing for a Sony Alpha NEX-5A will be considered a match for Sony Alpha NEX-5). The converse is not true – if a listing has less specificity than the the product, it will not be considered a match.  

In practice I imagine there will be counterexamples to the second assumption – I don't know enough about cameras to say if model codes are always prefix-free. Future work could include developing heuristics to determine whether trailing code information is trivial (e.g. a color code) or indicative of a fundamentally different product.

















