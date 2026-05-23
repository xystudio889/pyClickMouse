import json
import sys

def zip_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    with open(json_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
        
if __name__ == '__main__':
    zip_json(sys.argv[1])