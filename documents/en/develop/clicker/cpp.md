---
title: Python/pyd calling
description: Introduction to how to use Python to call pyd files.
layout: doc
---

<script setup>
    import important from '@theme/components/important.vue'
</script>

# header/dll calling

This article introduces how to use Python to call pyd files.

## Download

Go to [github releases](https://github.com/xystudiocode/pyClickMouse/releases), find latest version with .h or dll version files.

<important text='Important'>
In the following text, <code>CLICKMOUSE_CLASS</code> in dll refers to <code>int</code>, in header calling refers to <code>void</code>.
</important>

## Function Library

`ClickMouse` function:
- Definition:
```cpp
CLICKMOUSE_CLASS ClickMouse(
    unsinged int MouseButton, 
    unsigned int delay, 
    unsigned int pressTime, 
    int times = 1
)
```
- Parameters:
- - MouseButton: Pressed key, optional `LEFT` or `RIGHT`
- - delay: Click delay
- - time: Click count, default is 1 time, if `INFINITE` then infinite

`LeftClick` function:
```cpp
CLICKMOUSE_CLASS LeftClick(
    int times = 1, 
    unsigned int delay, 
    unsigned int pressTime
)
```
Equivalent to `ClickMouse(LEFT, delay, pressTime, times)`

`RightClick` function:
```cpp
CLICKMOUSE_CLASS RightClick(
    int times = 1, 
    unsigned int delay, 
    unsigned int pressTime
)
```
Equivalent to `ClickMouse(RIGHT, delay, pressTime, times)`

## Example
```cpp
#include <clickMouse.h>
#include <iostream>
using namespace std;

int main(){
    cout << CLICKMOUSE_VERSION << endl; // Print version information, if successfully output a string of numbers, then installation successful
    clickMouse(LEFT, 1000, 10, 10); // Click left button 10 times, interval 1000ms, press time 10ms
    return 0;
}
```
## Usage Priority
```mermaid
graph LR
C[C/C++] --> E[dll calling] --> D[command line calling]