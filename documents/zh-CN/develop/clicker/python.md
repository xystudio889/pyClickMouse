---
title: Python/pyd调用
description: 介绍如何使用Python调用pyd文件。
layout: doc
---

<script setup>
    import note from '@theme/components/note.vue'
</script>

# Python/pyd调用

本文介绍了如何使用Python调用pyd文件。

## 下载

### 库
运行`pip install clickmouse`,等待下载完成

<note title='批注'>
若你在中国，`pip`的速度较慢，你可以输入：

<pre><code class="language-bash">pip install -i https://pypi.tuna.tsinghua.edu.cn/simple clickmouse</code></pre>
</note>

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple clickmouse
```

### pyd
前往[github releases](https://github.com/xystudiocode/pyClickMouse/releases)，找到最新版本有pyd的版本文件。

::: warning 注意
请确保下载的是pyd文件。

pyd文件要和python的版本匹配，比如Python3.7要下载带有`cp37`的版本。

free threaded版本的pyd文件下载要带t，如3.14t要下载带有`cp314t`的版本。
:::

## 函数库

`click_mouse`函数：
- 定义：
```python
def click_mouse(
    button: Literal['left', 'right'], 
    delay: int, 
    time: int=1) -> None:
```
- 参数：
- - button:按下的键位，可选`clickmouse.LEFT`或`clickmouse.RIGHT`
- - delay:点击延迟
- - time:点击次数，默认为1次，如果是`clickmouse.INFINITE`则为无限 

## 示例

```python
import clickmouse

clickMouse.click_mouse(clickmouse.LEFT, 1000, 10, 10) # 连点10次左键，间隔为1000ms，按下间隔为10ms
```

## 使用优先级
```mermaid
graph LR
A[python] --> B[pyd调用] --> D[命令行调用]
```