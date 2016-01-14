import matching_helpers
import codecs
import json
import sys


def insert(mapping, manufacturer, family, model, product_name):
    """
    Add a new product to the tree.

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: frozenset(str) - Tokenized manufacturer field
    family: tuple(str) - Tokenized family field
    model: tuple(str) - Tokenized model field
    product_name: str -  Taken directly from JSON
    """
    if manufacturer not in mapping:
        mapping[manufacturer] = {}

    if family not in mapping[manufacturer]:
        mapping[manufacturer][family] = {}

    if model not in mapping[manufacturer][family]:
        mapping[manufacturer][family][model] = [product_name]


def match_on_manufacturer(mapping, manufacturer, description, price):
    """
    Returns the listing's manufacturer if found, None otherwise. First tries
    to match on the manufacturer field, and if that fails then try the
    description. If the latter route is taken some additional checks are made,
    as these items are often accessories.

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: tuple(str)
    description: tuple(str)
    price: float
    """ 
    hits = set()
           
    for known_manufacturer in mapping:

        if len(known_manufacturer.intersection(manufacturer)) > 0:
            hits.add(known_manufacturer)

    if not hits and matching_helpers.extra_manu_check(mapping, description, price):

        for known_manufacturer in mapping:

            if len(known_manufacturer.intersection(set(description))) > 0:
                hits.add(known_manufacturer)
    
    if len(hits) == 1:
        return list(hits)[0]


def match_on_family(mapping, manufacturer, description, max_fam):
    """
    Returns a list of families associated with this listing, or all if no
    particular family is found. Allows for multiple hits: inspection suggests
    there can be some overlap within good results. 

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: tuple(str) - The listing's manufacturer field, tokenized 
    description: tuple(str) - The listing's title field, tokenized
    max_fam: int - largest N such that some family name is an N-gram
    """ 
    hits = set([None])

    for i in range(0, len(description)):

        for j in range(i, i + (1 + max_fam)):

            if description[i:j] in mapping[manufacturer]:
                hits.add(description[i:j])

    return hits


def match_on_model(mapping, manufacturer, families, description, max_mod):
    """
    Returns a specific model associated with the listing, or None if zero or
    more than one matches are made. If there are overlapping matches, take
    the longest one. 

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: tuple(str) - the manufacturer found for this listing
    families: list(tuple(str) - families found in the description
    description: tuple(str) - the tokenized lisiting title
    max_mod: int - largest N such that some model code is an N-gram
    """ 
    hits, previous_end, previous_length = set(), -1, 0

    for family in families:
        
        for i in range(0, len(description)):
            longest_model_match = None
        
            for j in range(i, min(len(description), (1 + i + max_mod))):
 
                if family in mapping[manufacturer] and \
                   description[i:j] in mapping[manufacturer][family] and \
                   (i > previous_end or j - i >= previous_length):
                    longest_model_match = description[i:j]
                    previous_end, previous_length = j, j - i

            if longest_model_match:
                hits.add((family, longest_model_match))

    if len(hits) == 1:
        return list(hits)[0]

    else:
        return None, None

if __name__ == "__main__":

    # Dictionary Mapping Products to listings; counters
    mapping, max_fam, max_mod = {}, 0, 0

    with codecs.open('../input/products.txt', encoding='utf-8') as products:
        print 'Reading in products.txt, building tree...'

        for line in products:
            manufacturer, family, model, name = matching_helpers.parse_product(line)
            insert(mapping, manufacturer, family, model, name)

            # Keep track of max n-gram size for families and models
            if family and len(family) > max_fam:
                max_fam = len(family)

            if len(model) > max_mod:
                max_mod = len(model)

    with codecs.open('../input/listings.txt', encoding='utf-8') as listings:
        print 'Reading in listings.txt, generating matches...'

        for line in listings:
            manufacturer_field, description, price, listing = matching_helpers.parse_listing(line)
 
            # Level 1: Attempt to match manufacturer field
            manufacturer = match_on_manufacturer(mapping, manufacturer_field, description, price)

            # Level 2: Attempt to match on family 
            if manufacturer:
                families = match_on_family(mapping, manufacturer, description, max_fam)

                # Level 3: Attempt to match against a specific model
                family, model = match_on_model(mapping, manufacturer, families, description, max_mod)

                if model:
                    mapping[manufacturer][family][model].append(listing)

    with codecs.open('../output/results.json', 'w', encoding='utf-8') as outfile:
        print 'Writing results to file...'

        for manufacturer in mapping:

            for family in mapping[manufacturer]:

                for model in mapping[manufacturer][family]:
                    
                    result = mapping[manufacturer][family][model]
                    product_name, listings = result[0], result[1:]
                    result_object = {'product_name': product_name,
                                     'listings': listings}
                    line = json.dumps(result_object, ensure_ascii=False).encode('utf8')
                    outfile.write(unicode(line, 'utf-8') + '\n')
