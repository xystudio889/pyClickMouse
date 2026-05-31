---
title: 设置
description: 设置
layout: doc
---

<style>
.settings-general {
    content: url('/imgs/features/zh-CN/light/settings/general.png');
}

.dark .settings-general {
    content: url('/imgs/features/zh-CN/dark/settings/general.png')
}

.style {
    content: url('/imgs/features/zh-CN/light/settings/style.png');
}

.dark .style {
    content: url('/imgs/features/zh-CN/dark/settings/style.png')
}

.clicker {
    content: url('/imgs/features/zh-CN/light/settings/clicker.png');
}

.dark .clicker {
    content: url('/imgs/features/zh-CN/dark/settings/clicker.png')
}

.updater {
    content: url('/imgs/features/zh-CN/light/settings/update.png');
}

.dark .updater {
    content: url('/imgs/features/zh-CN/dark/settings/update.png')
}

.hotkey {
    content: url('/imgs/features/zh-CN/light/settings/hotkey.png');
}

.dark .hotkey {
    content: url('/imgs/features/zh-CN/dark/settings/hotkey.png')
}

.notify {
    content: url('/imgs/features/zh-CN/light/settings/notify.png');
}

.dark .notify {
    content: url('/imgs/features/zh-CN/dark/settings/notify.png')
}

.doc {
    content: url('/imgs/features/zh-CN/light/settings/document.png');
}

.dark .doc {
    content: url('/imgs/features/zh-CN/dark/settings/document.png')
}

.fupdate {
    content: url('/imgs/features/zh-CN/light/updater/fupdate.png');
}

.dark .fupdate {
    content: url('/imgs/features/zh-CN/dark/updater/fupdate.png')
}

.updateok {
    content: url('/imgs/features/zh-CN/light/updater/updateok.png');
}

.dark .updateok {
    content: url('/imgs/features/zh-CN/dark/updater/updateok.png')
}

.lab {
    content: url('/imgs/features/zh-CN/light/settings/lab.png')
}

.dark .lab {
    content: url('/imgs/features/zh-CN/dark/settings/lab.png')
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

# 设置

<important title="注意">有些设置项目可能需要进入测试版本打开部分实验项目才能启用。</important>

## 功能介绍

可以用来管理clickmouse运行时候的策略。

## 功能列表

- 常规设置：调整一些不在下面列表中的项目，如软件语言。
- 样式设置：设置clickmouse的主题、样式。
- 连点器设置：控制连点器的行为，如默认连点间隔、连点次数。
- 更新设置：用于控制clickmouse的更新服务，如是否自动更新、检查更新频率。
- 热键设置：用于控制热键功能，如左键连点、右键连点的热键。
- 文档设置：控制文档功能默认打开的网站。
- 通知设置：用于控制软件的通知提醒，如是否显示通知。

## 常规设置
常规设置包含了一些软件的基础设置，如软件语言等。

设置项目有：
- 软件语言：用于切换软件的语言，目前官方支持简体中文和英文。
- - 类型：下拉框
- - 默认值：系统语言
- - 可选值：根据语言包文件决定，官方支持`简体中文`和`英语`。
- - 字段名：`select_language`
::: tip 提示
切换语言后，软件需要重启才能生效。
:::
::: info 提示
如果自定义语言包没有及时更新，缺少新内容的翻译，新内容将会显示为英文。
:::
- 保留托盘图标：用于控制软件是否在任务栏显示图标；
- - 类型：开关
- - 默认值：开启
- - 字段名：`show_tray_icon`
<note title="提示">
<em>如果关闭保留托盘图标选项，托盘图标不会完全关闭，而是会在程序主窗口关闭后退出。</em>
</note>

- 开机自启动：如果勾选，软件会在系统启动时自动启动；
- - 默认值：关闭
- - 字段名：无，他依赖系统自身的开机自启动设置。
- 重置开机自启动配置：如果你的开机自启动会显示窗口或有其他问题，可以尝试点击这个按钮来修复。
- - 类型：按钮
- 软件反馈网址：控制在软件反馈时候打开的网址。
<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

- - 类型：输入框
- - 默认值：[链接](https://github.com/xystudiocode/pyClickMouse/issues/new/choose) `https://github.com/xystudiocode/pyClickMouse/issues/new/choose`
- - 字段名：`feedback`
- 重置反馈链接：重置软件反馈网站的链接。
<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

- - 类型：按钮
- 软件响应延迟：用于控制软件响应速度；*相应延迟越快，软件在切换样式的时候相应越快，但是CPU占用率也会越高。*
- - 类型：滑块
- - 默认值：100ms
- - 最小值：1ms
- - 最大值：1000ms
- - 间隔值：10ms
- - 字段名：`soft_delay`

- 无实验项时候隐藏“实验室”设置项：如果勾选，没有实验室设置项目时候，“实验室”设置项会被隐藏。
<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

- - 类型：开关
- - 默认值：开启
- - 字段名：`hide_flags`

- 重置所有设置：用于恢复默认设置，恢复后需要重启软件才能生效。
- - 类型：按钮

::: warning 警告
***设置的修改会立即生效，但是部分设置需要重启软件才能生效。***

这个操作会覆盖掉之前的设置，比较危险，请谨慎操作。
:::

<img class="settings-general" alt="常规设置" />

---

## 风格设置

风格设置用于调整软件的主题和样式。

设置项目有：
- 窗口样式：用于切换软件的窗口样式；
- - 类型：下拉框
- - 默认值：系统默认
- - 可选值：根据样式文件决定，官方支持根据系统颜色、浅色、深色
- - 字段名：`select_style`
- 使用windows强调色显示组件：控制组件是否使用windows强调色；关闭后使用clickmouse颜色。下面查看demo
- - 类型：开关
- - 默认值：开
- - 字段名：`use_windows_color`
<note title='提示'>
这个操作不会完全改变组件风格，选择框等组件仍会使用系统强调色
</note>

<div>
<p>颜色demo:</p>
<div class="button_bg button_bg_dark">
<button onclick="javascript:alert('你按下了深色主题的clickmouse颜色按钮！')" class="clickmouse_button clickmouse_color_button">深色主题的clickmouse颜色</button>
<button onclick="javascript:alert('你按下了深色主题的主题颜色按钮！')" class="clickmouse_button dark_accent_color">深色主题的windows主题颜色(主题颜色为默认颜色#0078d7)</button>
</div>
<div class="button_bg button_bg_light">
<button onclick="javascript:alert('你按下了浅色主题的clickmouse颜色按钮！')" class="clickmouse_button clickmouse_color_button">浅色主题的clickmouse颜色</button>
<button onclick="javascript:alert('你按下了浅色主题的主题颜色按钮！')" class="clickmouse_button light_accent_color">浅色主题的windows主题颜色(主题颜色为默认颜色#0078d7)</button>
</div>
</div>

- 窗口主题：设置窗口主题
- - 类型：下拉框
- - 默认值：根据系统版本决定：
- - - Windows 10：`Windows10`样式
- - - Windows 11：`Windows11`样式
- - - 其他windows：`Windows`样式
- - - 其他：`Fusion`样式
- - 可选值：根据系统决定，windows有：`windows标准样式`、`windows经典样式`、`windows Vista样式`和`Fusion样式`
- - 字段名：`theme`

::: warning 警告
部分主题不能很好的适配clickmouse的其他组件，如深色模式、反色模式等。
:::

<img class="style" alt="风格设置" />

## 连点器设置

可以设置连点器的一些参数，如连点间隔、连点次数等。

设置项目有：
- 连点延迟默认值：控制连点数字为空的时候的默认延迟
- - 类型：输入框
- - 默认值：空
- - 字段名：`click_delay`
- 连点延迟单位：控制默认延迟的单位
- - 类型：下拉框
- - 默认值：`毫秒`
- - 可选值：`毫秒`、`秒`
- - 字段名：`delay_unit`
- 连点延迟错误时候使用的默认值：如果开启，在连点延迟输入框输入错误的时候，会使用默认值
- - 类型：开关
- - 默认值：关
- - 字段名：`delay_error_use_default`
<note title='提示'>
此操作在<code>连点延迟</code>参数设置为空的时候禁用
</note>

<note title='提示'>
如果关闭此选项，只有在连点为空的时候才会使用默认值；开启后只要输入格式错误就会使用默认值。
</note>

- 连点次数默认值：控制连点次数为空的时候的默认次数
- - 类型：输入框
- - 默认值：空
- - 字段名：`click_times`
- 连点次数单位：控制默认连点次数的单位
- - 类型：下拉框
- - 默认值：`次`
- - 可选值：`次`、`万次`、`无限`
- - 字段名：`times_unit`
- 连点次数错误时候使用的默认值：如果开启，在连点次数输入框输入错误的时候，会使用默认值
- - 类型：开关
- - 默认值：关
- - 字段名：`times_error_use_default`
- 连点总耗时：通过软件连点次数和间隔，计算出的总耗时。
- - 类型：文本
- - 值：根据连点次数和间隔计算出来的总耗时
- - 字段名：无

<img class="clicker" alt="连点器设置" />

## 更新设置

用于控制软件的更新服务，如是否自动更新、检查更新频率。
设置项目有：
- 开启更新：如果开启，就可以管理下面的更新设置。
- - 类型：开关
- - 默认值：开
- - 字段名：`update_enabled`
<caution title='警告'>
我不建议关闭更新，这会让你的clickmouse有更多的问题。
</caution>

::: tip 提示
如果你发现检查更新提示：'更新未开启'，请打开这个设置。
:::

- 更新提示：如果关闭，那么看不到更新提示。‘
- - 类型：开关
- - 默认值：开
- - 字段名：`update_notify`

<img class="fupdate" alt="更新提示" />

<note title='提示'>
这个设置和更新完成提示独立，如果关闭此设置，更新完成提示也不会关闭。
</note>

- 静默更新：如果开启，那么软件更新时不会弹出提示框。
- - 类型：开关
- - 默认值：关
- - 字段名：`quiet_update`

<important title='提示'>
如果开启此设置，那么更新提示将会关闭，即使你开启了此设置。
</important>

- 更新完成提示：如果开启，那么更新完成后会弹出提示框。
- - 类型：开关
- - 默认值：开
- - 字段名：`update_ok_notify`

<img class="updateok" alt="更新完成弹窗" />

<note title='提示'>
这个弹窗会在静默更新完成后弹出。
</note>

::: tip 提示
下面的通知设置也受更新设置影响，如果是灰色，可能是因为更新服务未开启。
:::

<img class="updater" alt="更新设置" />

## 热键设置

用于设置软件的热键功能，如左键连点、右键连点的热键。

设置项目有：
- 热键启用：如果关闭，那么软件的热键功能将会关闭。
<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

- - 类型：开关
- - 默认值：开
- - 字段名：`hotkey_enabled`
- 左键连点热键：设置左键连点的热键。
- - 类型：输入框
- - 默认值：`F2`
- - 字段名：`left_click_hotkey`
- 右键连点热键：设置右键连点的热键。
- - 类型：输入框
- - 默认值：`F3`
- - 字段名：`right_click_hotkey`
- 暂停/重启连点热键：设置暂停/重启连点器的热键。
- - 类型：输入框
- - 默认值：`F4`
- - 字段名：`pause_click_hotkey`
- 停止连点热键：设置停止连点的热键。
- - 类型：输入框
- - 默认值：`F6`
- - 字段名：`stop_click_hotkey`
- 连点属性热键：设置打开连点属性的热键。
- - 类型：输入框
- - 默认值：`Ctrl+Alt+A`
- - 字段名：`click_attr_hotkey`
- 快速连点热键：设置打开快速连点的热键。
- - 类型：输入框
- - 默认值：`Ctrl+Alt+F`
- - 字段名：`fast_click_hotkey`
- 主窗口热键：设置打开主窗口的热键。
- - 类型：输入框
- - 默认值：`Ctrl+Alt+M`
- - 字段名：`main_window_hotkey`
- 重置左键连点设置：用于恢复默认左键连点设置。
- - 类型：按钮
- 重置右键连点设置：用于恢复默认右键连点设置。
- - 类型：按钮
- 重置暂停/重启连点设置：用于恢复默认暂停/重启连点设置。
- - 类型：按钮
- 重置停止连点设置：用于恢复默认停止连点设置。
- - 类型：按钮
- 重置连点属性设置：用于恢复默认连点属性设置。
- - 类型：按钮
- 重置快速连点设置：用于恢复默认快速连点设置。
- - 类型：按钮
- 重置主窗口设置：用于恢复默认主窗口设置。
- - 类型：按钮

<img class="hotkey" alt="热键设置" />

## 文档设置

用于设置文档功能默认打开的网站。

设置项目有：
- 文档默认连接：
- - 类型：输入框
- - 默认值：[链接](https://xystudiocode.github.io/pyClickMouse/{lang})`https://xystudiocode.github.io/pyClickMouse/{lang}`
- - 字段名：`doc_default_link`
- 重置文档默认链接：用于恢复默认文档默认链接。
<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

- - 类型：按钮

::: tip 提示
`{lang}`会被替换为当前软件语言，如`zh-CN`或`en`。
:::

- 文档语言：
- - 类型：下拉框
- - 默认值：软件语言
- - 可选值：`软件语言`、`系统语言`和根据软件支持的语言包(默认`简体中文`、`英语`)

- 更新日志路径：设置更新日志的路径。
- - 类型：输入框
- - 默认值：`updatelog`

::: tip 提示
软件的更新日志路径是相对于文档默认连接的路径，如默认的打开更新日志的链接是[链接](https://xystudiocode.github.io/pyClickMouse/{lang}/updatelog)`https://xystudiocode.github.io/pyClickMouse/{lang}/updatelog`，那么更新日志路径就填入`updatelog`。
:::

- 重置更新日志路径：用于恢复默认更新日志路径。
<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

- - 类型：按钮

> 这一段的{lang}也会被解析。

<img class="doc" alt="文档设置" />

## 通知设置

<note title="提示">这个设置项需要在实验室开启<code>More settings</code>才能启用</note>

用于控制软件的通知提醒，如是否显示通知。

设置项目有：

用于控制软件的更新服务，如是否自动更新、检查更新频率。
设置项目有：
- 开启更新：如果开启，就可以管理下面的更新设置。
- - 类型：开关
- - 默认值：开
- - 字段名：`update_enabled`
<caution title='警告'>
我不建议关闭更新，这会让你的clickmouse有更多的问题。
</caution>

<important title='重要'>
如果你发现检查更新提示：'更新未开启'，请打开这个设置。
</important>

- 更新提示：如果关闭，那么看不到更新提示。‘
- - 类型：开关
- - 默认值：开
- - 字段名：`update_notify`

<img class="fupdate" alt="更新提示" />

<note title='批注'>
如果开启此设置，那么更新提示将会关闭，即使你开启了此设置。
</note>

- 更新完成提示：如果开启，那么更新完成后会弹出提示框。
- - 类型：开关
- - 默认值：开
- - 字段名：`update_ok_notify`

<note title='提示'>
这个弹窗会在静默更新完成后弹出。
</note>

::: tip 提示
上面的更新设置也受通知设置影响，如果是灰色，可能是因为更新服务未开启。
:::

- 软件启动警告：如果开启，那么软件启动时资源丢失会弹出警告提示框。
- - 类型：开关
- - 默认值：开
- - 字段名：`show_warning`

::: info 提示
clickmouse在启动时候会检查资源，如果发现缺少了部分内容，就会弹出`软件启动警告`
:::

- 官方扩展包丢失警告：如果开启，那么软件启动时官方扩展包丢失会弹出警告提示框。
- - 类型：开关
- - 默认值：开
- - 字段名：`show_package_warning`

<img class="notify" alt="通知设置" />

## 实验室

将会测试新的功能

因为会随版本更新测试项，所以不例举设置项了。

<img class="lab" alt="实验室" />

## 使用方法

1. 打开设置-设置选项
2. 在左侧选择要切换设置的选项
3. 点击右侧的开关/输入框以切换设置