import re

def test_main():
    re_code = re.compile(r'-re\d+$') # 移除-re后缀
    assert re_code.sub('', '3.2.0.18beta3-re1') == '3.2.0.18beta3'
    assert re_code.sub('', '3.2.0.18beta3-re11') == '3.2.0.18beta3'
    assert re_code.sub('', '3.2.0.18-re11393') == '3.2.0.18'