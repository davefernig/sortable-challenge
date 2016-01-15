import matching_helpers
import codecs
import json
import sys
import os


def insert(mapping, manufacturer, family, model, product_name):
    """
    Add a new product to the tree

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: str - manufacturer field
    family: tuple(str) - tokenized family field
    model: tuple(str) - tokenized model field
    product_name: str -  taken directly from JSON
    """
    if manufacturer not in mapping:
        mapping[manufacturer] = {}

    if family not in mapping[manufacturer]:
        mapping[manufacturer][family] = {}

    if model not in mapping[manufacturer][family]:
        mapping[manufacturer][family][model] = [product_name]


def match_on_manufacturer(mapping, manufacturer, title, price):
    """
    Returns the listing's manufacturer if found, None otherwise

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: str - listing manufacturer field
    title: tuple(str) - tokenized title field
    price: float
    """
    if manufacturer not in mapping:

        if title[0] in mapping and price > 30.0:
            manufacturer = title[0]

        else:
            manufacturer = None

    return manufacturer


def match_on_family(mapping, manufacturer, title, max_fam):
    """
    Returns a list of families associated with this listing

    PARAMS
    ------------------------------
    mapping : nested dict - main data structure
    manufacturer: tuple(str) - listing manufacturer field 
    title: tuple(str) -  tokenized title field
    max_fam: int - largest N such that some family name is an N-gram
    """ 
    families = set([None])

    for i in range(0, len(title)):

        for j in range(i, i + (1 + max_fam)):

            if title[i:j] in mapping[manufacturer]:
                families.add(title[i:j])

    return families


def match_on_model(mapping, manufacturer, families, title, max_mod):
    """
    Returns the model if exactly one is found, otherwise returns None. 

    PARAMS
    ------------------------------
    mapping : nested dict - Main data structure
    manufacturer: str - the manufacturer found for this listing
    families: list(tuple(str) - families found in the title
    title: tuple(str) - tokenized lisiting title
    max_mod: int - largest N such that some model code is an N-gram
    """ 
    models, previous_end, previous_length = set(), -1, 0

    for family in families:
        
        for i in range(0, len(title)):
            longest_model_match = None
        
            for j in range(i, min(len(title), (1 + i + max_mod))):
 
                if family in mapping[manufacturer] and \
                   title[i:j] in mapping[manufacturer][family] and \
                   (i > previous_end or j - i >= previous_length):
                    longest_model_match = title[i:j]
                    previous_end, previous_length = j, j - i

            if longest_model_match:
                models.add((family, longest_model_match))

    if len(models) == 1:
        return models.pop()

    else:
        return None, None

if __name__ == "__main__":

    if not os.path.exists('../output/'):
        os.makedirs('../output/')

    version = sys.version_info[0]

    if version == 2:
        string_convert = unicode

    if version == 3:
        string_convert = str

    # Dictionary Mapping Products to listings; counters
    mapping, max_fam, max_mod = {}, 0, 0

    with codecs.open('../input/products.txt', encoding='utf-8') as products:
        print('Reading in ../input/products.txt, building tree...')

        for line in products:
            manufacturer, family, model, name = matching_helpers.parse_product(line)
            insert(mapping, manufacturer, family, model, name)

            # Keep track of max n-gram size for families and models
            if family and len(family) > max_fam:
                max_fam = len(family)

            if len(model) > max_mod:
                max_mod = len(model)

    with codecs.open('../input/listings.txt', encoding='utf-8') as listings:
        print('Reading in ../input/listings.txt, generating matches...')

        for line in listings:
            listing, manufacturer_field, title, price = matching_helpers.parse_listing(line)
 
            # Level 1: Attempt to match manufacturer field
            manufacturer = match_on_manufacturer(mapping, manufacturer_field, title, price)

            # Level 2: Attempt to match on family 
            if manufacturer:
                families = match_on_family(mapping, manufacturer, title, max_fam)

                # Level 3: Attempt to match against a specific model
                family, model = match_on_model(mapping, manufacturer, families, title, max_mod)

                if model:
                    mapping[manufacturer][family][model].append(listing)

    with codecs.open('../output/results.json', 'w', encoding='utf-8') as outfile:
        print('Writing results to ../output/results.json')

        for manufacturer in mapping:

            for family in mapping[manufacturer]:

                for model in mapping[manufacturer][family]:
                    
                    result = mapping[manufacturer][family][model]
                    product_name, listings = result[0], result[1:]
                    result_object = {'product_name': product_name, 'listings': listings}
                    line = json.dumps(result_object, ensure_ascii=False).encode('utf8')
                    outfile.write(string_convert(line, 'utf-8') + '\n')
