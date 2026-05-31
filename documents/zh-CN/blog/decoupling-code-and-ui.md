---
title: Decoupling code and ui
layout: doc
---

# ui和代码解耦

## 背景

- 为了增加可扩展性，用户可以导入其他玩家的gui文件。
- 减少代码冗余

## 结果

把所有ui控制的代码都移动到`res/ui/`下的gui文件，这样就可以通过导入其他玩家的gui文件来扩展功能。

把源码本身变成一个代码库，通过`name`的组件名字属性来修改操作

## 格式

`gui`文件采用json格式，类似：

```json
{
  "name": "layout",
  "value": {
    "direction": "h",
    "content": [
      {
        "name": "button",
        "value": {
          "type": "QPushButton",
          "args": ["hello"],
          "style": "selected",
          "init_steps": { "setFixedHeight": [30], "setFixedWidth": [100] }
        }
      },
      {
        "name": "label",
        "value": {
          "type": "QLabel",
          "args": ["world"],
          "style": "big_text_16",
          "init_steps": { "setFixedHeight": [30], "setFixedWidth": [100] }
        }
      }
    ]
  }
}
```

## 启用方法

<details><summary>最低要求的clickmouse版本</summary>
<p style="color:gray;">
Clickmouse测试版, >=3.3.0.23alpha5
</p>
</details> 

打开主程序设置，找到`实验室`，勾选`Decoupling UI and program`，重启程序。