import codecs
import json
import sys
import os
import re

# For string substitution in listings
listing_subs = {u'\xb5' : ' mju ',
                ' dsc' : ' cybershot dsc ',
                'cyber shot' : ' cybershot ',
                'power shot' : ' powershot ',                
                'digital ixus' : ' ixus ',
                'dmc' : ' lumix dmc ',
                'konica minolta|konica|minolta': ' konicaminolta '}

manu_subs = {'hewlett packard' : ' hp ',
             'konica minolta|konica|minolta': ' konicaminolta '}

family_subs = {'cyber shot' : ' cybershot ',
               'power shot' : ' powershot ',
               'digital ixus' : 'ixus'}


def tokenize_code(code):
    """
    Split a code into parts, e.g. "SH-100x becomes "sh 100 x"
    """
    return tuple(re.findall(r"[^\W\d_]+|\d+", code.lower(), re.U))


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
    result = result.split()[0] if result.split() else ''
    return result


def parse_product(line):
    """
    Parse a line in the products file into a tuple of manufacturer, family,
    model, and name.
    """
    product = json.loads(line)    
    manu = tokenize_manu(product['manufacturer'])  
    family = tokenize_and_sub(product, 'family', family_subs) if 'family' in product else None
    model = tokenize_code(product['model'])
    name = product['product_name']  
    return manu, family, model, name


def parse_listing(line):
    """
    Attempt to parse listing.
    """
    listing = json.loads(line)
    manu = tokenize_manu(listing['manufacturer'])
    title = tokenize_and_sub(listing, 'title', listing_subs)
    price = float(listing['price'])
    return listing, manu, title, price


def tokenize_and_sub(tree, field, sublist):
    """
    Tokenize and make substitutions for 
    """
    result = tokenize_code(tree[field])
    return tuple(make_substitutions(' '.join(result), sublist).split())
