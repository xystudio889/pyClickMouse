# ClickMouse API工具库

使用clickmouse api来实现clickmouse扩展开发！
导入方法：
```python
from clickmouse_APIv1 as clickmouse
```
语言包格式:
```json
[
    {
        "lang_id": 0,
        "lang_system_name":"en",
        "lang_package": {
            "01": "This is the language package file",
        }
    },
    {
        "lang_id": 1,
        "lang_system_name": "zh-CN",
        "lang_package": {
            "01": "这是语言包文件",
        }
    }
]
```
编辑扩展完成后，打包为exe,使用clickmouse导入测试
若clickmouse已经安装，设置的数据将会导入到clickmouse中