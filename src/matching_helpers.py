import codecs
import json
import os
import re
import sys

# Special characters for string replacement in listings
family_special_chars = {'cybershot': ['cyber', 'shot']}
model_special_chars = {u'\xb5' : ['mju'], 
                       'dsc': ['cyber', 'shot', 'dsc'], 
                       'cybershot': ['cyber', 'shot']}
manu_special_chars = {frozenset(['hewlett', 'packard']) : frozenset(['hp'])}

def tokenize_manu(line):
    """
    Returns the frozenset of tokens for matching on manufacturer
    """
    result = frozenset(line.lower().split())

    for sc_set in manu_special_chars:
        
        if sc_set.issubset(result):
            return manu_special_chars[sc_set]
        
    return result


def tokenize_code(code, replace=None):
    """
    Split an alphanumeric item code into parts
    e.g. "SH-100x becomes ['sh', '100', 'x']"
    """
    current_type, separated_code = char_type(code[0]), ''

    for char in code.lower():

        if char_type(char) != current_type:
            separated_code += ' '

        if char_type(char) >= 0:
            separated_code += char

        current_type = char_type(char)

    result = separated_code.split()
    
    if replace:
        listing_result = []    

        for i in range(0, len(result)):
         
            if result[i] in replace:
                listing_result += replace[result[i]]
             
            else:
                listing_result.append(result[i])

        result = listing_result

    return tuple(result)


def parse_product(line):
    """
    Parse a line in the products file into a tuple of manufacturer, family,
    model, and name.
    """
    product = json.loads(line)
    name = product['product_name']
    manu = tokenize_manu(product['manufacturer'])
    model = tokenize_code(product['model'])
    fam = tokenize_code(product['family'], replace=family_special_chars) if 'family' in product else (None)
    return manu, fam, model, name


def parse_listing(line):
    """
    Attempt to parse listing.
    """
    listing = json.loads(line)
    manu = tokenize_manu(listing['manufacturer'])
    title = listing['title'].lower().split()
    description = reduce(lambda a, s: a + list(tokenize_code(s, replace=model_special_chars)), title, [])
    price = float(listing['price'])
    return manu, tuple(description), price, listing


def char_type(char):
    """
    Return relevant character type
    """
    if char.isalpha():
        return 0

    elif char in [str(x) for x in range(0, 10)]:
        return 1

    else:
        return -1


def extra_manu_check(mapping, description, price):
    """
    Extra conditions for listings with an unknown manufacturer
    """
    if frozenset([description[0]]) not in mapping:
        return False

    if price <= 30.0:
        return False

    return True

