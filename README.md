# Sortable Coding Challenge
My entry to the Sortable Coding Challenge. It is a hashing solution with rule-based pre-processing. It runs in linear time, given some basic assumptions (more details below). On my machine (1.7GHz) it takes 3.3s with Python 2 (and 3s with Python 3).

## Requires
Python 2 or Python 3. (I've tested with 2.7 and 3.4. If you encounter version compatibility issues, let me know and I'll find a fix!)

## Usage

Clone the repository, navigate to src, and run parse.py: 
```
cd sortable-challenge/src/
python parse.py
```
Output will be written to sortable-challenge/output/results.json. The paths to input and output files are specified in parse.py.  

To visually examine the results (one product at a time), use:
```
python inspect.py results.json
```
To visually compare the differences between the output of different versions (analogous to the command line tool diff), use:
```
python compare.py results_v1.json results_v2.json
```

##Implementation Details

### Pre-processing
- Strings are split on alphabetic-numeric boundaries prior to tokenization (e.g. so that "XL-200s" is equivalent to "xl 200 s") 
- Some substitutions are made (e.g. 'Hewlett Packard' is replaced by 'hp').

### Data structures and algorithms
The items in products.txt are hashed into a tree with a hierarchichal structure: manufacturer, family, product, and associated listings. Then listings.txt is read, each listing is parsed, and an attempt is made to match the manufacturer, family, and model.

- To match manufacturers, first try the manufacturer field. If that fails try the first token of the title, but only use this if the price exceeds a threshold (an unknown manufacturer often indicates a third-party accessory, and these are usually cheaper).

- Assuming we have hit on a manufacturer, we try to match against that manufacturer's families. We check every n-gram in the title (where n runs through 1 to the size of the longest family name in products.txt). Here we allow for multiple hits.

- Last, we try to match on a specific model in the same fashion. Each token can only contribute to one model – if there are overlapping model codes we take the longest. If we get exactly one hit, we add that listing to the branch.  

### Efficiency
Each product is processed and hashed once. Each listing is processed once. The number of times we attempt to hash it only depends on the length of its title, the number of families the manufacturer produces, and the largest n-gram family size. If these have constant bounds, then the program runs in O(m + n), where m is the number of products and n is the number of listings.  

## Assumptions
I made following assumptions:

1. For each product, we want to recall every listing whose contents are a superset of that product (and no other product). The contents must include the product itself – if the listing is only for an accessory we don't want to recall it.

2. We want to recall all variants of a given product (e.g. A listing for a Sony Alpha NEX-5A will match Sony Alpha NEX-5). The converse is not true – if a listing has less specificity than the the product, it will not be considered a match.  

In practice I imagine there might be counterexamples to the second assumption – I don't know enough about cameras to say if model codes are always prefix-free. Future work could include developing heuristics to determine whether trailing code information is trivial (e.g. a color code) or indicative of a fundamentally different product.

















