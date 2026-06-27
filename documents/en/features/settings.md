---
title: Settings
description: Settings
layout: doc
---

<style>
.settings-general {
    content: url('/imgs/features/en/light/settings/general.png');
}

.dark .settings-general {
    content: url('/imgs/features/en/dark/settings/general.png')
}

.style {
    content: url('/imgs/features/en/light/settings/style.png');
}

.dark .style {
    content: url('/imgs/features/en/dark/settings/style.png')
}

.clicker {
    content: url('/imgs/features/en/light/settings/clicker.png');
}

.dark .clicker {
    content: url('/imgs/features/en/dark/settings/clicker.png')
}

.updater {
    content: url('/imgs/features/en/light/settings/update.png');
}

.dark .updater {
    content: url('/imgs/features/en/dark/settings/update.png')
}

.hotkey {
    content: url('/imgs/features/en/light/settings/hotkey.png');
}

.dark .hotkey {
    content: url('/imgs/features/en/dark/settings/hotkey.png')
}

.notify {
    content: url('/imgs/features/en/light/settings/notify.png');
}

.dark .notify {
    content: url('/imgs/features/en/dark/settings/notify.png')
}

.doc {
    content: url('/imgs/features/en/light/settings/document.png');
}

.dark .doc {
    content: url('/imgs/features/en/dark/settings/document.png')
}

.fupdate {
    content: url('/imgs/features/en/light/updater/fupdate.png');
}

.dark .fupdate {
    content: url('/imgs/features/en/dark/updater/fupdate.png')
}

.updateok {
    content: url('/imgs/features/en/light/updater/updateok.png');
}

.dark .updateok {
    content: url('/imgs/features/en/dark/updater/updateok.png')
}

.lab {
    content: url('/imgs/features/en/light/settings/lab.png')
}

.dark .lab {
    content: url('/imgs/features/en/dark/settings/lab.png')
}

.clickmouse_button {
    border: 1px solid;
    border-radius: 4px;
    padding: 5px 15px;
    height: 23px;
    font-size: 9pt;
    line-height: 12px;
    font-family: 'Segoe UI' 'Microsoft YaHei';
    margin: 15px 15px;
    margin-top: 0;
}

.clickmouse_color_button {
    background-color: dodgerblue;
    color: white;
    border: #2a7bca;
}

.clickmouse_color_button:hover {
    background-color: #30a0f0
}

.clickmouse_color_button:active {
   background-color: #2078c5
}

.dark_accent_color {
    background-color: #4eb0fe;
    color: black;
    margin-bottom: 5px;
}

.dark_accent_color:hover {
    background-color: #5cb7ff;
}

.dark_accent_color:active {
    background-color:  #0064b3;
}

.light_accent_color {
    background-color: #0078d7;
    color: white;
}

.light_accent_color:hover {
    background-color: #4eb0fe;
}

.light_accent_color:active {
    background-color: #0064b3;
}

.button_bg {
   display:flex;
   flex-wrap:wrap;
   flex-direction:column;
   align-items: center;
   width: 100%;
   margin:0;
   padding-top: 10px;
   margin-bottom: 15px; 
}

.button_bg_light { 
   background-color: #f3f3f3;
}

.button_bg_dark { 
   background-color: #202020;
}
</style>

<script setup>
    import important from '@theme/components/important.vue'
    import tip from '@theme/components/tip.vue'
    import note from '@theme/components/note.vue'
    import info from '@theme/components/info.vue'
    import caution from '@theme/components/caution.vue'
</script>

# Settings

<important title="Tip">Some settings items need beta version and open some developing features to enable.</important>

## Function Description

Can be used to manage clickmouse's operation strategies.

## Function List

- General Settings: Adjust some items not in the list below, such as software language.
- Style Settings: Set clickmouse's theme, style.
- Clicker Settings: Control clicker behavior, such as default click interval, click count.
- Update Settings: Used to control clickmouse's update service, such as whether to auto-update, update check frequency.
- Hotkey Settings: Used to control hotkey functions, such as left click, right click hotkeys.
- Documentation Settings: Control documentation function default opened website.
- Notification Settings: Used to control software notification reminders, such as whether to show notifications.

## General Settings
General settings include some basic software settings, such as software language, etc.

Setting items include:
- Software Language: Used to switch software language, currently officially supports Simplified Chinese and English.
- - Type: Dropdown box
- - Default value: System language
- - Optional values: Determined by language pack files, officially supports `Simplified Chinese` and `English`.
- - Field name: `select_language`
::: tip Tip
After switching language, software needs to restart to take effect.
:::
::: info Tip
If custom language pack is not updated in time, lacking translation for new content, new content will display in English.
:::
- Keep Tray Icon: Used to control whether software shows icon in taskbar;
- - Type: Checkbox
- - Default value: On
- - Field name: `show_tray_icon`
<note title="Tip">
<em>If turn off Keep Tray Icon option, tray icon will not completely close, but will exit after program main window closes.</em>
</note>

- Auto-start on Boot: If checked, software will automatically start when system boots;
- - Default value: Off
- - Field name: None, it depends on system's own auto-start settings.
- Reset Auto-start Configuration: If your auto-start shows window or has other issues, you can try clicking this button to repair.
- - Type: Button
- Software Feedback URL: Controls the URL opened during software feedback.
<note title="Tip">This setting item needs to enable <code>More settings</code> to enable.</note>

- - Type: Input box
- - Default value: [link](https://github.com/xystudiocode/pyClickMouse/issues/new/choose) `https://github.com/xystudiocode/pyClickMouse/issues/new/choose`
- - Field name: `feedback`
- Reset feedback URL: Reset the feedback URL to default value.
<note title="Tip">This setting item needs to enable <code>More settings</code> to enable.</note>

- - Type: Button
- Software Response Delay: Used to control software response speed; *Faster response delay means faster response when switching styles, but CPU usage will also be higher.*
- - Type: Slider
- - Default value: 100ms
- - Minimum value: 1ms
- - Maximum value: 1000ms
- - Interval value: 10ms
- - Field name: `soft_delay`

- Hide "lab" tab when no experimental features: If checked, "lab" tab will be hidden when no experimental features.
<note title="Tip">This setting item needs to enable <code>More settings</code> to enable.</note>

- - Type: Checkbox
- - Default value: On
- - Field name: `hide_flags`

- Reset All Settings: Used to restore default settings, after restoration need to restart software to take effect.
- - Type: Button

::: warning Warning
***Settings modifications take effect immediately, but some settings require restarting software to take effect.***

This operation will overwrite previous settings, relatively dangerous, please operate carefully.
:::

<img class="settings-general" alt="General Settings" />

---

## Style Settings

Style settings used to adjust software theme and style.

Setting items include:
- Window Style: Used to switch software window style;
- - Type: Dropdown box
- - Default value: System default
- - Optional values: Determined by style files, officially supports according to system color, light, dark
- - Field name: `select_style`
- Use Windows accent color to display components: Control whether components use Windows accent color; after turning off, use clickmouse color. See demo below
- - Type: Checkbox
- - Default value: On
- - Field name: `use_windows_color`
<note title='Tip'>
This operation will not completely change component style, checkboxes and other components will still use system accent color
</note>

<div>
<p>Color demo:</p>
<div class="button_bg button_bg_dark">
<button onclick="javascript:alert('You pressed dark theme clickmouse color button!')" class="clickmouse_button clickmouse_color_button">Dark theme clickmouse color</button>
<button onclick="javascript:alert('You pressed dark theme theme color button!')" class="clickmouse_button dark_accent_color">Dark theme Windows theme color (theme color is default color #0078d7)</button>
</div>
<div class="button_bg button_bg_light">
<button onclick="javascript:alert('You pressed light theme clickmouse color button!')" class="clickmouse_button clickmouse_color_button">Light theme clickmouse color</button>
<button onclick="javascript:alert('You pressed light theme theme color button!')" class="clickmouse_button light_accent_color">Light theme Windows theme color (theme color is default color #0078d7)</button>
</div>
</div>

- Window Theme: Set window theme
- - Type: Dropdown box
- - Default value: Determined by system version:
- - - Windows 10: `Windows10` style
- - - Windows 11: `Windows11` style
- - - Other Windows: `Windows` style
- - - Other: `Fusion` style
- - Optional values: Determined by system, Windows has: `Windows standard style`, `Windows classic style`, `Windows Vista style` and `Fusion style`
- - Field name: `theme`

::: warning Warning
Some themes cannot adapt well to other clickmouse components, such as dark mode, inverted color mode, etc.
:::

<img class="style" alt="Style Settings" />

## Clicker Settings

Can set some clicker parameters, such as click interval, click count, etc.

Setting items include:
- Click Delay Default Value: Control default delay when click number is empty
- - Type: Input box
- - Default value: Empty
- - Field name: `click_delay`
- Click Delay Unit: Control default delay unit
- - Type: Dropdown box
- - Default value: `Millisecond`
- - Optional values: `Millisecond`, `Second`
- - Field name: `delay_unit`
- Default Value Used When Click Delay Error: If enabled, when click delay input box input error, will use default value
- - Type: Checkbox
- - Default value: Off
- - Field name: `delay_error_use_default`

<note title='Tip'>
This operation is disabled when <code>Click Delay</code> parameter is set to empty
</note>

<note title='Tip'>
If turn off this option, only when click is empty will use default value; after enabling, as long as input format error will use default value.
</note>

- Modify click attributes using the default values: If enabled, then in the click delay change, the default value will continue to use.
- - Type：Checkbox
- - Field name: Off
- - Field name: `modify_using_default_input`
- Modify click units using the default values: If enabled, then in the unit change, the default value will continue to use.
- - Type：Checkbox
- - Field name: Off
- - Field name: `modify_using_default_combo`
- Click Count Default Value: Control default count when click count is empty
- - Type: Input box
- - Default value: Empty
- - Field name: `click_times`
- Click Count Unit: Control default click count unit
- - Type: Dropdown box
- - Default value: `Times`
- - Optional values: `Times`, `Ten thousand times`, `Infinite`
- - Field name: `times_unit`
- Default Value Used When Click Count Error: If enabled, when click count input box input error, will use default value
- - Type: Checkbox
- - Default value: Off
- - Field name: `times_error_use_default`
- Total Click Time: Total time calculated through software click count and interval.
- - Type: Text
- - Value: Total time calculated based on click count and interval
- - Field name: None

<img class="clicker" alt="Clicker Settings" />

## Update Settings

Used to control software's update service, such as whether to auto-update, update check frequency.
Setting items include:
- Enable Update: If enabled, can manage update settings below.
- - Type: Checkbox
- - Default value: On
- - Field name: `update_enabled`
<caution title='Caution'>
I do not recommend turning off updates, this will cause more problems for your clickmouse.
</caution>

::: tip Tip
If you find check update prompt: 'Update not enabled', please turn on this setting.
:::

- Update Notification: If turned off, then cannot see update notification.
- - Type: Checkbox
- - Default value: On
- - Field name: `update_notify`

<img class="fupdate" alt="Update Notification" />

<note title='Tip'>
This setting is independent of update completion notification, if turn off this setting, update completion notification will also not turn off.
</note>

- Silent Update: If enabled, then software update will not pop up notification box.
- - Type: Checkbox
- - Default value: Off
- - Field name: `quiet_update`

<important title='Tip'>
If enable this setting, then update notification will be turned off, even if you enabled this setting.
</important>

- Update Completion Notification: If enabled, then after update completion will pop up notification box.
- - Type: Checkbox
- - Default value: On
- - Field name: `update_ok_notify`

<img class="updateok" alt="Update Completion Popup" />

<note title='Tip'>
This popup will appear after silent update completion.
</note>

::: tip Tip
The notification settings below are also affected by update settings, if grayed out, may be because update service not enabled.
:::

<img class="updater" alt="Update Settings" />

## Hotkey Settings

Used to set software's hotkey functions, such as left click, right click hotkeys.

Setting items include:
- Hotkey Enabled: If turned off, then software's hotkey function will be turned off.
<note title="Tip">This setting item needs to enable <code>More settings</code> to enable.</note>

- - Type: Checkbox
- - Default value: On
- - Field name: `hotkey,hotkey_enabled`
- Left Click Hotkey: Set left click hotkey.
- - Type: Input box
- - Default value: `F2`
- - Field name: `hotkey,hotkeys,left_click_hotkey`
- Right Click Hotkey: Set right click hotkey.
- - Type: Input box
- - Default value: `F3`
- - Field name: `hotkey,hotkeys,right_click_hotkey`
- Pause/Restart Click Hotkey: Set pause/restart clicker hotkey.
- - Type: Input box
- - Default value: `F4`
- - Field name: `hotkey,hotkeys,pause_click_hotkey`
- Stop Click Hotkey: Set stop click hotkey.
- - Type: Input box
- - Default value: `F6`
- - Field name: `hotkey,hotkeys,stop_click_hotkey`
- Click Attribute Hotkey: Set open click attribute hotkey.
- - Type: Input box
- - Default value: `Ctrl+Alt+A`
- - Field name: `hotkey,hotkeys,click_attr_hotkey`
- Main Window Hotkey: Set open main window hotkey.
- - Type: Input box
- - Default value: `Ctrl+Alt+M`
- - Field name: `hotkey,hotkeys,main_window_hotkey`
- Reset Left Click Settings: Used to restore default left click settings.
- - Type: Button
- Reset Right Click Settings: Used to restore default right click settings.
- - Type: Button
- Reset Pause/Restart Click Settings: Used to restore default pause/restart click settings.
- - Type: Button
- Reset Stop Click Settings: Used to restore default stop click settings.
- - Type: Button
- Reset Click Attribute Settings: Used to restore default click attribute settings.
- - Type: Button
- Reset Fast Click Settings: Used to restore default fast click settings.
- - Type: Button
- Reset Main Window Settings: Used to restore default main window settings.
- - Type: Button

<img class="hotkey" alt="Hotkey Settings" />

## Documentation Settings

Used to set documentation function default opened website.

Setting items include:
- Documentation Default Link:
- - Type: Input box
- - Default value: [link](https://xystudiocode.github.io/pyClickMouse/{lang})`https://xystudiocode.github.io/pyClickMouse/{lang}`
- - Field name: `doc_default_link`
- Reset documentation default link: Used to restore default documentation default link.
<note title="Tip">This setting item needs to enable <code>More settings</code> to enable.</note>

- - Type: Button
::: tip Tip
`{lang}` will be replaced with current software language, such as `zh-CN` or `en`.
:::

- Documentation Language:
- - Type: Dropdown box
- - Default value: Software language
- - Optional values: `Software language`, `System language` and according to software supported language packs (default `Simplified Chinese`, `English`)

- Update Log Path: Set update log path.
- - Type: Input box
- - Default value: `updatelog`
- Reset update log path: Used to restore default update log path.
<note title="Tip">This setting item needs to enable <code>More settings</code> to enable.</note>

- - Type: Button

::: tip Tip
Software's update log path is relative to documentation default link path, such as default open update log link is [link](https://xystudiocode.github.io/pyClickMouse/{lang}/updatelog)`https://xystudiocode.github.io/pyClickMouse/{lang}/updatelog`, then update log path fill in `updatelog`.
:::

> This section's {lang} will also be parsed.

<img class="doc" alt="Documentation Settings" />

## Notification Settings

Used to control software's notification reminders, such as whether to show notifications.

Setting items include:

Used to control software's update service, such as whether to auto-update, update check frequency.
Setting items include:
- Enable Update: If enabled, can manage update settings below.
- - Type: Checkbox
- - Default value: On
- - Field name: `update_enabled`
<caution title='Caution'>
I do not recommend turning off updates, this will cause more problems for your clickmouse.
</caution>

<important title='Important'>
If you find check update prompt: 'Update not enabled', please turn on this setting.
</important>

- Update Notification: If turned off, then cannot see update notification.
- - Type: Checkbox
- - Default value: On
- - Field name: `update_notify`

<img class="fupdate" alt="Update Notification" />

<note title='Note'>
If enable this setting, then update notification will be turned off, even if you enabled this setting.
</note>

- Update Completion Notification: If enabled, then after update completion will pop up notification box.
- - Type: Checkbox
- - Default value: On
- - Field name: `update_ok_notify`

<note title='Tip'>
This popup will appear after silent update completion.
</note>

::: tip Tip
The update settings above are also affected by notification settings, if grayed out, may be because update service not enabled.
:::

- Software Startup Warning: If enabled, then when software starts, resource loss will pop up warning notification box.
- - Type: Checkbox
- - Default value: On
- - Field name: `show_warning`

::: info Tip
clickmouse checks resources when starting, if finds missing some content, will pop up `Software Startup Warning`
:::

- Official Extension Package Missing Warning: If enabled, then when software starts, official extension package missing will pop up warning notification box.
- - Type: Checkbox
- - Default value: On
- - Field name: `show_package_warning`

<img class="notify" alt="Notification Settings" />

## Lab

To test new features.

Because the test items will be updated with each version, the settings items are not listed.

<img class="lab" alt="Lab" />

## Usage Method

1. Open Settings - Settings options
2. On left side select option to switch settings
3. Click switch/input box on right side to toggle settings