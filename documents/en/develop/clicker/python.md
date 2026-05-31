---
title: Python/pyd calling
description: Introduction to how to use Python to call pyd files.
layout: doc
---

<script setup>
    import note from '@theme/components/note.vue'
</script>

# Python/pyd calling

This article introduces how to use Python to call pyd files.

## Download

### Library
Run `pip install clickmouse`, wait for download to complete

<note title='Note'>
If you are in China, `pip` speed is slow, you can enter:

<pre><code class="language-bash">pip install -i https://pypi.tuna.tsinghua.edu.cn/simple clickmouse</code></pre>
</note>

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple clickmouse
```

### pyd
Go to [github releases](https://github.com/xystudiocode/pyClickMouse/releases), find latest version with pyd version files.

::: warning Note
Please ensure downloading pyd files.

pyd files need to match python version, for example Python3.7 needs to download version with `cp37`.

free threaded version pyd files download needs to include t, such as 3.14t needs to download version with `cp314t`.
:::

## Function Library

`click_mouse` function:
- Definition:
```python
def click_mouse(
    button: Literal['left', 'right'], 
    delay: int, 
    time: int=1) -> None:
```
- Parameters:
- - button: Pressed key, optional `clickmouse.LEFT` or `clickmouse.RIGHT`
- - delay: Click delay
- - time: Click count, default is 1 time, if `clickmouse.INFINITE` then infinite

## Example

```python
import clickmouse

clickMouse.click_mouse(clickmouse.LEFT, 1000, 10, 10) # Click left button 10 times, interval 1000ms, press interval 10ms
```

## Usage Priority
```mermaid
graph LR
A[python] --> B[pyd calling] --> D[command line calling]