from base64 import b64decode, b64encode
import json

byte_text = [0x00, 0x43, 0x4C, 0x49, 0x4B, 0x59, 0x02, 0x01]

def encrypt():
    # 读取原始数据
    with open('key.json', 'r', encoding='utf-8') as f:
        keys = json.load(f)
    
    # 构建带分隔符的字符串
    sep_mid = '\x02\x45\x4f\x4e\x02\x00'  # 键值分隔符
    sep_end = '\x03\x45\x4f\x50\x02\x00'   # 条目结束符
    entries = [f"{k}{sep_mid}{v}" for k, v in keys.items()]
    raw_str = sep_end.join(entries) + sep_end
    
    # 双层Base64编码
    b64_str = b64encode(raw_str.encode()).decode()
    processed_bytes = bytes([(ord(c) + 189) % 256 for c in b64_str])
    
    # 合成最终字节流
    final_data = bytearray(byte_text) + processed_bytes
    
    # 写入文件（附加Base64编码层）
    with open('key', 'wb') as f:
        f.write(b64encode(final_data))

byte_text = [0x00, 0x43, 0x4C, 0x49, 0x4B, 0x59, 0x02, 0x01]

def decrypt():
    with open('key', 'r') as f:
        encrypted_data = b64decode(f.read())
    
    # 分离固定头部和加密内容
    encrypted_bytes = encrypted_data[8:]
    
    # 逆向字节转换
    decrypted_b64 = bytes([(b - 189) % 256 for b in encrypted_bytes]).decode('latin-1')
    
    # Base64解码原始数据
    original_str = b64decode(decrypted_b64).decode('utf-8')
    
    # 分割键值对
    sep_mid = '\x02\x45\x4f\x4e\x02\x00'
    sep_end = '\x03\x45\x4f\x50\x02\x00'
    keys = {}
    
    for entry in original_str.split(sep_end)[:-1]:
        if sep_mid in entry:
            key, value = entry.split(sep_mid, 1)
            keys[key] = value
    
    return keys

if __name__ == '__main__':
    encrypt()