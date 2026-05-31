---
title: clickmouse Clicker Introduction
description: Introduction to ClickMouse clicker
layout: doc
---

# Introduction

clickmouse library is an open source mouse control library, can perform mouse click operations.

## clickmouse library

clickmouse library is a library for controlling mouse, can simulate mouse click operations.

Select documentation on the right for reference.

## Calling Methods
Calling methods include:
- ✅ C/C++ header file calling Using original C++ version clickMouse modified Fastest speed, best compatibility, but highest possibility of usage failure. Can download from [releases](https://github.com/xystudiocode/pyClickMouse/releases)
- ✅ Using original C++ version clickMouse Fastest speed, best compatibility, but highest possibility of usage failure, already stopped updating, can download from [releases](https://github.com/xystudiocode/pyClickMouse/releases), [previous clickmouse project](https://github.com/xystudio889/ClickMouse)
- ✅ Using .dll calling Based on C++ language, fastest speed, better compatibility, highest possibility of usage failure. (Configuration more difficult, recommend using C/C++ header files) Can download from [releases](https://github.com/xystudiocode/pyClickMouse/releases)
- ✅ (Developer recommended) python calling Medium speed, best compatibility, lowest possibility of usage failure. Can use `pip install clickmouse` to download
- ✅ Using .pyd calling Based on python language, faster speed, poorer compatibility (different python versions may not be compatible), lower possibility of usage failure. Can download from [releases](https://github.com/xystudiocode/pyClickMouse/releases) (separate compilation only needs to compile cython/ directory)
- ❌ Using standard command line Based on python language. ~~Will be included in GUI version and pip installation version~~ Temporarily no such version, please stay tuned

## Usage Priority
```mermaid
graph LR
A[python] --> B[pyd calling] --> D[command line calling]
C[C/C++] --> E[dll calling] --> D