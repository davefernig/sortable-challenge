import json
import sys

filename = sys.argv[1]
output_path = '../output/'

with open(output_path + filename) as infile:

    for line in infile:
        obj = json.loads(line)
        print obj['product_name'], ',', len(obj['listings']), 'listings found'
        
        for listing in obj['listings']:
            print '    ', listing
        raw_input('---------------------------------------PRESS ENTER TO CONTINUE---------------------------------------')
