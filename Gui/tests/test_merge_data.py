def merge_lists_dicts(*dicts):
    '''
    合并多个字典，每个字典的值都是列表
    
    Params:
    *dicts: 任意数量的字典，每个字典的值都是列表
    
    Returns:
    合并后的字典，每个键对应的值是列表，列表中元素不重复
    
    Raises:
    ValueError: 输入的字典中有重复元素
    TypeError: 输入的字典不是字典
    '''
    if len(dicts) < 2:
        raise ValueError('At least two dictionaries are required')
    
    for d in dicts:
        if not isinstance(d, dict):
            raise TypeError(f'Value {d} is not a dictionary')
            
    # 1. 收集所有键
    all_keys = set()
    for d in dicts:
        all_keys.update(d.keys())
    
    # 2. 合并每个键对应的列表
    merged_result = {}
    for key in all_keys:
        merged_list = []
        for d in dicts:
            if key in d:
                merged_list.extend(d[key])
        
        # 对合并后的列表去重（保留1个）
        deduplicated = []
        seen = set()
        for item in merged_list:
            if item not in seen:
                seen.add(item)
                deduplicated.append(item)
        
        merged_result[key] = deduplicated
    
    # 3. 检查不同键之间是否有重复元素
    # 构建元素到键的映射
    element_to_keys = {}
    for key, values in merged_result.items():
        for value in values:
            if value in element_to_keys:
                # 如果元素已经出现过，检查是否是同一个键
                if key not in element_to_keys[value]:
                    # 同一个元素出现在不同键中，报错
                    raise ValueError(
                        f'The merged result contains duplicate items: the element {value} appears in keys {element_to_keys[value]} and {key}'
                    )
            else:
                element_to_keys[value] = {key}
    
    return merged_result

# 测试用例
def test_merge_lists_dicts():
    print('测试1：正常合并')
    dict1 = {'a': [1, 2], 'b': [3, 4]}
    dict2 = {'a': [1, 2, 6], 'b': [4, 5], 'c': [7, 8]}
    result = merge_lists_dicts(dict1, dict2)
    print(f'输入: dict1={dict1}, dict2={dict2}')
    print(f'输出: {result}')
    assert result == {'a': [1, 2, 6], 'b': [3, 4, 5], 'c': [7, 8]}
    
    print('\n测试2：应该报错的情况')
    dict3 = {'a': [1, 2, 3], 'b': [3, 4]}
    dict4 = {'a': [1, 2], 'b': [4, 5], 'c': [7, 8]}
    try:
        result = merge_lists_dicts(dict3, dict4)
        print(f'输出: {result}')
        raise AssertionError('测试失败: 应该抛出ValueError')
    except ValueError as e:
        print(f'错误: {e}')
    # 预期: 报错，因为元素3同时出现在a和b中
    
    print('\n测试3：多个字典合并')
    dict5 = {'a': [1, 2], 'b': [3, 4]}
    dict6 = {'a': [2, 5], 'c': [6, 7]}
    dict7 = {'b': [4, 8], 'c': [7, 9], 'd': [10]}
    result = merge_lists_dicts(dict5, dict6, dict7)
    print(f'输入: dict5={dict5}, dict6={dict6}, dict7={dict7}')
    print(f'输出: {result}')
    assert result == {'a': [1, 2, 5], 'b': [3, 4, 8], 'c': [6, 7, 9], 'd': [10]}
    # 预期: {'a': [1, 2, 5], 'b': [3, 4, 8], 'c': [6, 7, 9], 'd': [10]}
    
    print('\n测试4：空字典和单字典')
    try:
        result1 = merge_lists_dicts({})
        print(f'空字典: {result1}')
        raise AssertionError('测试失败: 应该抛出ValueError')
    except ValueError as e:
        print(f'错误: {e}')
    # 预期: 报错，因为只有一个输入
    
    try:
        result2 = merge_lists_dicts({'a': [1, 1, 2, 2], 'b': [3, 4]})
        print(f'单字典（含重复）: {result2}')
        raise AssertionError('测试失败: 应该抛出ValueError')
    except ValueError as e:
        print(f'错误: {e}')
    # 预期: 报错，因为只有一个输入
    
    print('\n测试5：相同元素在不同键中（应该报错）')
    dict8 = {'x': [1, 2], 'y': [2, 3]}
    try:
        result = merge_lists_dicts(dict8)
        print(f'输出: {result}')
        raise AssertionError('测试失败: 应该抛出ValueError')
    except ValueError as e:
        print(f'错误: {e}')
    # 预期: 报错，因为元素2同时出现在x和y中}
    
    print('\n测试6：多个空字典')
    result3 = merge_lists_dicts({}, {}, {})
    result4 = merge_lists_dicts({}, {})
    print(f'多个空字典: 三个：{result3}, 二个：{result4}')
    assert not result3
    assert not result4
    print('测试7：空字典和非空字典')
    dict9 = {'a': [1, 2], 'b': [3, 4]}
    result5 = merge_lists_dicts({}, dict9)
    print(f'空字典和非空字典: {result5}')
    dict10 = {'a': [1, 2], 'b': [3, 4]}
    dict11 = {'a': [2, 5], 'c': [6, 7]}
    result6 = merge_lists_dicts(dict10, dict11, {})
    print(f'2个字典: {result5}')
    print(f'3个字典: {result6}')
    assert result5 == {'a': [1, 2], 'b': [3, 4]}
    assert result6 == {'a': [1, 2, 5], 'b': [3, 4], 'c': [6, 7]}
    print('测试8：单个字典和一个数字')
    try:
        result7 = merge_lists_dicts({'a': [1, 2]}, 1)
        print(f'单个字典和一个数字: {result7}')
        raise AssertionError('测试失败: 应该抛出TypeError')
    except TypeError as e:
        print(f'错误: {e}')