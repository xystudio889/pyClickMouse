from sharelibs import get_resource_path
import json

if __name__ == "__main__":
    # 压缩语言包
    with open(get_resource_path('langs.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(get_resource_path('langs.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)