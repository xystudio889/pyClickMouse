def contains_substring(str_list, target_str):
    '''
    检查目标字符串是否包含列表中的任意一个子串
    
    Params:
    str_list: 字符串列表，包含要查找的子串
    target_str: 目标字符串
    
    Returns:
    bool: 如果目标字符串包含列表中的任意一个子串则返回True，否则返回False
    '''
    return any(substring in target_str for substring in str_list)

def test_contains_substring():
    '''
    测试函数 contains_substring
    '''
    # 测试示例
    test_cases = [
        (['a', 'b'], 'abc', True),        # 应该返回 True ('a'在'abc'中)
        (['abd', 'cd'], 'cbd', True),     # 应该返回 False
        (['hello', 'world'], 'hello world', True),  # 应该返回 True
        ([], 'abc', False),                # 空列表应该返回 False
        (['xyz'], 'abc', False),           # 没有匹配应该返回 False
        (['ab', 'bc'], 'abc', True),      # 应该返回 True ('ab'在'abc'中)
    ]

    for lst, text, result in test_cases:
        result = contains_substring(lst, text)
        print(f'列表: {lst}, 字符串: "{text}" => {result}')
        assert result == result