from sharelibs import get_resource_path
import json

def zip_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__ == "__main__":
    zip_json(get_resource_path('package_info.json'))