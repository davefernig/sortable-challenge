import codecs
import json
import sys
import os
import re

# For string substitution in listings
listing_subs = {u'\xb5' : ' mju ',
                ' dsc' : ' cybershot dsc ',
                'cyber shot' : ' cybershot ',
                'power shot' : ' powershot '}

manu_subs = {'hewlett packard' : ' hp '}

family_subs = {'cyber shot' : ' cybershot ',
               'power shot' : ' powershot '}

def tokenize_code(code):
    """
    Split an alphanumeric item code into parts
    e.g. "SH-100x becomes "sh 100 x"
    """
    current_type, separated_code = char_type(code[0]), ''

    for char in code.lower():

        if char_type(char) != current_type:
            separated_code += ' '

        if char_type(char) >= 0:
            separated_code += char

        current_type = char_type(char)
    
    return separated_code.split()


def make_substitutions(sentence, subs):
    """
    Make the substitutions defined in sublist in tokens
    """
    for word in subs:
        sentence = re.sub(word, subs[word], sentence)

    return sentence


def tokenize_manu(line):
    """
    Returns the frozenset of tokens for matching on manufacturer
    """
    result = make_substitutions(line.lower(), manu_subs)        
    return frozenset(result.split())


def parse_product(line):
    """
    Parse a line in the products file into a tuple of manufacturer, family,
    model, and name.
    """
    product = json.loads(line)
    
    name = product['product_name']
    
    manu = tokenize_manu(product['manufacturer'])
    
    model = tuple(tokenize_code(product['model']))
    
    family = None

    if 'family' in product:
        family = product['family'].split()
        family = reduce(lambda a, s: a + tokenize_code(s), family, [])
        family = tuple(make_substitutions(' '.join(family), family_subs).split())

    return manu, family, model, name


def parse_listing(line):
    """
    Attempt to parse listing.
    """
    listing = json.loads(line)

    manu = tokenize_manu(listing['manufacturer'])

    #title = ' '.join(map(tokenize_code, listing['title'].split()))
    #title = tuple(make_substitutions(title, listing_subs).split())

    title = listing['title'].split()
    title = reduce(lambda a, s: a + tokenize_code(s), title, [])
    title = tuple(make_substitutions(' '.join(title), listing_subs).split())

    price = float(listing['price'])

    return manu, title, price, listing


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

