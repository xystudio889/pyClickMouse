---
title: Decoupling code and ui
layout: doc
---

# Decoupling UI and program

## Background

- To increase extensibility, users can import other player's gui files.
- To reduce code redundancy.

## Result

Move all ui control code to `res/ui/` directory, so that other player's gui files can be imported to extend the functionality.

Make the source code a code library, and modify the operation through the `name` component attribute.

## Format

The `gui` file is in json format, like:

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

## Enable method

<details><summary>Minimum required clickmouse version</summary>
<p style="color:gray;">
Clickmouse beta, >=3.3.0.23alpha5
</p>
</details> 
Open the main program settings, find `Labs`, check `Decoupling UI and program`, restart the program.