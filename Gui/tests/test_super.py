class B:
    def __init__(self, b_arg):
        print("B init")
        self.b_value = b_arg

class C:
    def __init__(self, c_arg):
        print("C init")
        self.c_value = c_arg

class A(B, C):
    def __init__(self, b_arg, c_arg, a_arg):
        # 显式调用 B 和 C 的初始化
        B.__init__(self, b_arg)
        C.__init__(self, c_arg)
        print("A init")
        self.a_value = a_arg

def test_super():
    # 测试
    a = A("B data", "C data", "A data")
    print(a.b_value)  # B data
    print(a.c_value)  # C data
    print(a.a_value)  # A data