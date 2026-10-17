---
title: Decoupling UI and program
layout: doc
---

# Decoupling UI and program

## Reason

- To increase extensibility, users can import other player's gui files.
- To reduce code redundancy.

## Result

Move all ui control code to `res/ui/` directory, so that other player's gui files can be imported to extend the functionality.

Make the source code a code library, and modify the operation through the `name` component attribute.

## Format

<del>The `.gui` file is in json format, like:<br />
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

> **Note**: We abandoned the `json` format and switched to `uiml`

`.gui` files use `uiml`, a highly extensible Qt UI language we developed ourselves, similar to:

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

## Enable method

<details><summary>Minimum required clickmouse version</summary>
<p style="color:gray;">
Clickmouse beta, >=3.3.0.23alpha5
</p>
</details> 
Open the main program settings, find `Labs`, check `Decoupling UI and program`, restart the program.