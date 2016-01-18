# Sortable Coding Challenge

UPDATE: After submitting my solution on Friday, I was curious to see what other people had done, and looked at some other repos. I thought I would list some observations and final thoughts: 

1. One obvious improvement to my implementation was using a trie (prefix-tree) to store model codes for faster matching. I was curious to see how much-speed up this would give, so I spent Sunday afternoon rolling up a trie implementation. It resulted in a significant reduction in runtime (about 30%). I've added the script (though it is admittedly a little coarse) to /src_update/trie_parse.py.

2. In my original implementation I was careful to provide a solution that is bounded by O(m + n), where m is the number of products in products.txt and n is the number of listings. This is because I knew I was only dealing with a subset of the data, and it would be safest to make sure everything scales linearly. However, in practice, m will grow far more slowly than n (assuming m even grows at all). If we know a bound on m, it might turn out to be worthwhile developing a solution that depends multiplicatively on m for gains in accuracy. It also might be worth hard-coding more rules based on the specific product set. For example, by concatenating bigram family names and assuming all family names are unigram, I was able to get the runtime below 2s. Of course, this sort of thing won't generalize to new product sets.

3. While writing the trie implementation, I noticed that there are examples of model codes in the dataset that are prefixes of others. This might mean that my second assumption (i.e. that we want to recall all variants of a model, full discussion below) results in an intolerably high false positive rate. Whether or not this happens essentially depends on how exhaustive our list of products is. By way of example: consider the Canon T3 and Canon T3i. Because both are in products.txt, if we see a listing for a T3i, this algorithm will match on T3i (and not T3). However, if T3i was not in products.txt it would (incorrectly) match on T3.

4. It appears that the Samsung SL 202 appears twice in products.txt (lines 186 and 258). By convention, my scripts match listings for this product to the product name on line 186.

5. I found and fixed a minor bug (loop boundary) in parse.py. The fix can be about at /src_update/fixed_parse.py It affected 27 listings. I didn't notice it originally because it prevented the matching of listings where model codes are at the very end – often accessories – so ironically the bug was improving perfomance. In general, it seems like leveraging word-positional information would be a smart way to reduce false positives. I felt [this entry](https://github.com/aaronlevin/sortable) made cool use of this idea.

Below is my original readme.

Dave Fernig, Jan 16, 2016

My entry to the Sortable Coding Challenge. It is a hashing solution with rule-based pre-processing. It runs in linear time, given some basic assumptions (more details below). On my machine (1.7GHz) it takes 3.3s.

## Requires
Python 2

## Usage

Clone the repository, navigate to src, and run parse.py: 
```
cd sortable-challenge/src/
python parse.py
```
The paths to input and output files are specified in parse.py. To visually examine the results (one product at a time), use:
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

















