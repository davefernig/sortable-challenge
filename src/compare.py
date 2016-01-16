import json
import sys
    
def msg(s0, s1, f0):

    if len(s0.difference(s1)) > 0:
        print(f0 + ' contains more entries for: ' + product + '\n')

        for item in s0.difference(s1):
            print(str(item))

        print("----------------------Press Enter to continue, 's' to see listings these files share, q to quit----------------------")
        
        response = raw_input()

        if response == 'q':
            sys.exit()

        if response == 's':
            for item in s0.intersection(s1):
                print(str(item))

            print("----------------------Press Enter to continue, q to quit----------------------")      
            
            if raw_input() == 'q':
                sys.exit()

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:\npython compare.py name_of_result_file name_of_different_result_file\n")
        sys.exit()

    filename_0, filename_1 = sys.argv[1], sys.argv[2]

    d0, d1, length_0, length_1 = {}, {}, 0, 0

    output_path = '../output/'

    with open(output_path + filename_0) as infile:
        for line in infile:
            obj = json.loads(line)
            d0[obj['product_name']] = obj['listings']
            length_0 += len(obj['listings'])        

    with open(output_path + filename_1) as infile:
        for line in infile:
            obj = json.loads(line)
            d1[obj['product_name']] = obj['listings']
            length_1 += len(obj['listings'])

    print(filename_0 + ' contains ' + str(length_0) + ' matches')
    print(filename_1 + ' contains ' + str(length_1) + ' matches')

    for product in d0:
        d0_listings, d1_listings = set([]), set([])
        
        for item in d0[product]:
            d0_listings.add( (item['title'], item['price']) )

        for item in d1[product]:
            d1_listings.add( (item['title'], item['price']) )

        msg(d0_listings, d1_listings, filename_0)
        msg(d1_listings, d0_listings, filename_1)

