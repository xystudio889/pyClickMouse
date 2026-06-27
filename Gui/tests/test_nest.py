def set_nested_value(dic: dict, path: str, mode:str, value) -> None:
    '''
    在字典中按路径设置值。
    - 如果路径不含逗号，则直接设置 dic[path] = value。
    - 如果路径含逗号，则按逗号分割为多级键，逐层递进，在最后一级键处设置值。
    若中间键不存在，则自动创建新字典；若中间键存在但不是字典，则覆盖为字典（原值丢失）。
    '''
    def check_dic(dic, path, val):
        if mode == 'set':
            dic[path] = val
        elif mode == 'del':
            del dic[path]
        else:
            raise ValueError('Invalid mode: ' + mode)

    if ',' not in path:
        check_dic(dic, path, value)
        return

    keys = [k.strip() for k in path.split(',')]  # 去除可能的空格
    current = dic
    # 逐层深入到倒数第二个键
    for key in keys[:-1]:
        if key not in current:
            check_dic(current, key, {})
        elif not isinstance(current[key], dict):
            raise ValueError('Invalid path: ' + path)  # 路径中存在无效的键
        current = current[key]
    # 在最后一级键处赋值
    check_dic(current, keys[-1], value)

def test_main():
    dic = {'a': {'b': {'c': 1}}}
    set_nested_value(dic, 'a,b,c', 'set', 2)
    print(dic)  # 输出 {'a': {'b': {'c': 2}}}
    assert dic['a']['b']['c'] == 2
    set_nested_value(dic, 'a,b,c', 'del', None)
    print(dic)  # 输出 {'a': {'b': {}}}
    assert 'c' not in dic['a']['b']
    set_nested_value(dic, 'a,d', 'set', 3)
    assert dic['a']['d'] == 3
    print(dic)  # 输出 {'a': {'b': {}, 'd': 3}}

if __name__ == '__main__':
    test_main()