import random

str_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f']

# 生成随机四位hex

string = ''

for i in range(4):
    string += random.choice(str_list)

print(string)  # 输出随机四位hex