import json
import sys

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:\npython inspect.py name_of_result_file\n")
        sys.exit()

    filename = sys.argv[1]
    output_path = '../output/'
    version = sys.version_info[0]

    if version == 2:
        get_response = raw_input

    if version == 3:
        get_response = input

    with open(output_path + filename) as infile:

        for line in infile:
            obj = json.loads(line)
            print(obj['product_name'] + ' , ' + str(len(obj['listings'])) + ' listings found')
        
            for listing in obj['listings']:
                print('    ' + str(listing))
        
            print('---------------------------------------Press Enter to continue, q to quit---------------------------------------')
            response = get_response()

            if response == 'q':
                sys.exit()
