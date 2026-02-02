from base64 import b64decode, b64encode

byte_text = [0x00, 0x43, 0x4C, 0x49, 0x4B, 0x59, 0x02, 0x01]
sep_mid = '\x02\x45\x4f\x4e\x02\x00'  # 键值分隔符
sep_end = '\x03\x45\x4f\x50\x02\x00'   # 条目结束符

def encrypt(keys):
    entries = [f"{k}{sep_mid}{v}" for k, v in keys.items()] # 键值对列表
    raw_str = sep_end.join(entries) + sep_end
    
    # 双层Base64编码
    b64_str = b64encode(raw_str.encode()).decode()
    processed_bytes = bytes([(ord(c) + 189) % 256 for c in b64_str])
    
    # 合成最终字节流
    final_data = bytearray(byte_text) + processed_bytes
    
    # 写入文件（附加Base64编码层）
    return b64encode(final_data)

def decrypt(encrypted_data):
    # 第一层：Base64解码
    layer1 = b64decode(encrypted_data)
    
    # 移除开头的固定字节头（byte_text部分）
    if list(layer1[:8]) == byte_text:
        processed_bytes = layer1[8:]
    else:
        # 如果没有找到预期的字节头，直接使用全部数据
        processed_bytes = layer1
    
    # 第二层：逆向字符变换
    # 加密时是 (ord(c) + 189) % 256，解密时是 (b - 189) % 256
    b64_str = ''.join([chr((b - 189) % 256) for b in processed_bytes])
    
    # 第三层：Base64解码
    raw_bytes = b64decode(b64_str)
    
    # 第四层：解码为字符串并解析键值对
    raw_str = raw_bytes.decode('utf-8')
    
    # 分割条目（注意：加密时每个条目都以sep_end结束）
    # 最后一个sep_end应该被移除，因为它是整体的结束符
    entries = raw_str.rstrip(sep_end).split(sep_end)
    
    # 解析每个键值对
    result = {}
    for entry in entries:
        if sep_mid in entry:
            key, value = entry.split(sep_mid, 1)  # 只分割第一个sep_mid
            result[key] = value
        
        return result

if __name__ == '__main__':
    data = {} # 替换为key
    
    print(encrypt(data)) # 加密
