from collections import defaultdict
import matching_helpers
import codecs
import json
import sys
import os

# PARAMS
input_path = '../input/'
output_path = '../output/'
products_file = 'products.txt' 
listings_file = 'listings.txt'
output_file = 'trie_results.json'


def insert(mapping, manufacturer, family, model_code, product_name):
    """
    Add a new product to the tree

    PARAMS
    ------------------------------
    mapping : dict - tree of products
    manufacturer: str - manufacturer field
    family: tuple(str) - tokenized family field
    model_code: tuple(str) - tokenized model field
    product_name: str -  taken directly from JSON
    """
    if manufacturer not in mapping:
        mapping[manufacturer] = {}

    if family not in mapping[manufacturer]:
        mapping[manufacturer][family] = {}

    matching_helpers.model_insert(mapping[manufacturer][family], 
                                      model_code, 
                                      product_name)


def match_on_manufacturer(mapping, manufacturer, title, price):
    """
    Returns the listing's manufacturer if found, None otherwise

    PARAMS
    ------------------------------
    mapping : dict - tree of products
    manufacturer: str - listing manufacturer field
    title: tuple(str) - tokenized title field
    price: float - listing price
    """
    if manufacturer not in mapping:

        if title[0] in mapping and price >= 30.0:
            manufacturer = title[0]

        else:
            manufacturer = None

    return manufacturer


def match_on_family(mapping, manufacturer, title, max_fam):
    """
    Returns a list of families associated with this listing

    PARAMS
    ------------------------------
    mapping : dict - tree of products
    manufacturer: str - listing manufacturer field 
    title: tuple(str) - tokenized title field
    max_fam: int - largest N such that some family name is an N-gram
    """
     
    families = set([None])

    for i in range(0, len(title)):

        for j in range(i, i + (1 + max_fam)):

            if title[i:j] in mapping[manufacturer]:
                families.add(title[i:j])

    return families


def match_on_model(mapping, manufacturer, families, title):
    """
    Returns the model if exactly one is found, otherwise returns None. 

    PARAMS
    ------------------------------
    mapping : dict - tree of products
    manufacturer: str - listing manufacturer field
    families: list(tuple(str) - families found in title
    title: tuple(str) - tokenized lisiting title
    max_mod: int - largest N such that some model code is an N-gram
    """ 

    if None not in mapping[manufacturer]:
        families.remove(None)

    models = set()

    for family in families:
        trie, start_index = mapping[manufacturer][family], 0    
        previous_end = -1

        while start_index < len(title):
            i = start_index            

            while i <= len(title):
                longest_model_match = None

                # If there is a product, keep track of it
                if 'PRODUCT_NAME' in trie:
                    longest_model_match = trie['PRODUCT_NAME']

                # If we have a match, keep looking
                if i < len(title) and title[i] in trie:
                    trie = trie[title[i]]
                    i += 1

                # No match: Add product if it is not a suffix, reset trie and counter
                else:
                    
                    if longest_model_match and i > previous_end:
                        models.add(longest_model_match)
                        previous_end = i

                    start_index += 1
                    trie = mapping[manufacturer][family]
                    break
    
    if len(models) == 1:
        return models.pop()

    else:
        return None

if __name__ == "__main__":

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Dictionary Mapping Products to listings; counters
    mapping, output_map, max_fam = {}, {}, defaultdict(int)

    with codecs.open(input_path + products_file, encoding='utf-8') as products:
        print('Reading in ' + input_path + products_file + ', building tree...')

        for line in products:
            manufacturer, family, model, name = matching_helpers.parse_product(line)
            insert(mapping, manufacturer, family, model, name)
            if name != 'Samsung_SL202':
                output_map[name] = []

            # Keep track of max n-gram size for families
            if family and len(family) > max_fam[manufacturer]:
                max_fam[manufacturer] = len(family)

    with codecs.open(input_path + listings_file, encoding='utf-8') as listings:
        print('Reading in ' + input_path + listings_file + ', generating matches...')

        for line in listings:
            listing, manufacturer_field, title, price = matching_helpers.parse_listing(line)
 
            # Level 1: Attempt to match manufacturer field
            manufacturer = match_on_manufacturer(mapping, manufacturer_field, title, price)

            # Level 2: Attempt to match on family 
            if manufacturer:
                families = match_on_family(mapping, manufacturer, title, max_fam[manufacturer])

                # Level 3: Attempt to match against a specific model
                model = match_on_model(mapping, manufacturer, families, title)

                if model:
                    output_map[model].append(listing)

    with codecs.open(output_path + output_file, 'w', encoding='utf-8') as outfile:
        print('Writing results to ' + output_path + output_file)

        for product_name in output_map:
            result_object = {'product_name': product_name, 'listings': output_map[product_name]}
            line = json.dumps(result_object, ensure_ascii=False).encode('utf8')
            outfile.write(unicode(line, 'utf-8') + '\n')
