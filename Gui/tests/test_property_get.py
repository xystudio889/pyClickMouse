class TestPropertyGet:
    @property
    def my_property(self):
        return "Hello World"
    
def test_property_get():
    obj = TestPropertyGet()
    print(obj.my_property)
    assert obj.my_property == "Hello World"
    
    print(getattr(obj, "my_property"))
    assert getattr(obj, "my_property") == "Hello World"