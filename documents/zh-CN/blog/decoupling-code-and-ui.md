---
title: 前后端分离
layout: doc
---

# 前后端分离

## 原因

- 为了增加可扩展性，用户可以导入其他玩家的gui文件。
- 减少代码冗余

## 结果

把所有ui控制的代码都移动到`res/ui/`下的gui文件，这样就可以通过导入其他玩家的gui文件来扩展功能。

把源码本身变成一个代码库，通过`name`的组件名字属性来修改操作

## 格式
<del>`gui`文件采用json格式，类似：<br />
{<br />
&nbsp;&nbsp;"name": "layout",<br />
&nbsp;&nbsp;"value": {<br />
&nbsp;&nbsp;&nbsp;&nbsp;"direction": "h",<br />
&nbsp;&nbsp;&nbsp;&nbsp;"content": [<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"name": "button",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"value": {<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"type": "QPushButton",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"args": ["hello"],<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"style": "selected",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"init_steps": { "setFixedHeight": [30], "setFixedWidth": [100] }<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"name": "label",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"value": {<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"type": "QLabel",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"args": ["world"],<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"style": "big_text_16",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"init_steps": { "setFixedHeight": [30], "setFixedWidth": [100] }<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br />
&nbsp;&nbsp;&nbsp;&nbsp;]<br />
&nbsp;&nbsp;}<br />
}<br />
</del><br />
> **批注**： 我们放弃了 `json` 格式，转向了 `uiml`

`.gui`文件采用 `uiml`，一种我们自研的高扩展Qt UI语言，类似：

```xml
<layout name='central_layout' direction='v'>
    <QLabel name='left_clicked' args=['!lang 0d'] />
    <QLabel name='right_clicked' args=['!lang 0e'] />
    <QLabel name='paused' args=['!lang 71'] />
    <QLabel name='stopped' args=['!lang 73'] />
    <QLabel name='click_delay' args=['!lang 78'] />
    <QLabel name='click_times' args=['!lang 5c'] />
    <QLabel name='total_run_time' args=['!lang 2c'] />
    <layout name='bottom_layout' direction='h' stretch='true' stretch_place='start'>
        <QPushButton name='ok_button' args=['!lang 1e'] style='selected' signals={'clicked': self.close} />
    </layout>
</layout>
```

## 启用方法

<details><summary>最低要求的clickmouse版本</summary>
<p style="color:gray;">
Clickmouse测试版, >=3.3.0.23alpha5
</p>
</details> 

打开主程序设置，找到`实验室`，勾选`Decoupling UI and program`，重启程序。