import json
from sharelibs import get_resource_path

with open(get_resource_path('dev_data.json'), 'r', encoding='utf-8') as f:
    dev_data = json.load(f) # 读取规则

def write(bytes:list[int]):
    '''写入数据到文件'''
    array = bytearray(bytes)
    with open('dev.dat', 'wb') as f:
        f.write(array)
        
def parse():
    '''解析数据'''
    config = {}
    
    try:
        with open('dev.dat', 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        data = b'\x00' * len(dev_data)

    # 解析数据
    for index, i in enumerate(dev_data):
        value = data[index]
        print(value)
        for k, v in i['cases'].items():
            k = int(k)
            if value == k:
                config[i['config_in_data']] = v

    return config