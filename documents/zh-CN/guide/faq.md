---
layout: doc
title: 常见问题
---

<style>
    .input_disable {
        content: url('/imgs/faq/zh-CN/light/input_disable.png')
    }

    .dark .input_disable {
        content: url('/imgs/faq/zh-CN/dark/input_disable.png')
    }

    .ipk_not_found {
        content: url('/imgs/faq/zh-CN/light/ipk_not_found.png')
    }

    .dark .ipk_not_found {
        content: url('/imgs/faq/zh-CN/dark/ipk_not_found.png')
    }

    .stop_click {
        content: url('/imgs/faq/zh-CN/light/stop_click.png')
    }

    .dark .stop_click {
        content: url('/imgs/faq/zh-CN/dark/stop_click.png')
    }

    .update_disable {
        content: url('/imgs/faq/zh-CN/light/update_disable.png')
    }

    .dark .update_disable {
        content: url('/imgs/faq/zh-CN/dark/update_disable.png')
    }

    .lang_not_found {
        content: url('/imgs/faq/light/lang_not_found.png')
    }

    .dark .lang_not_found {
        content: url('/imgs/faq/dark/lang_not_found.png')
    }
</style>

<script setup>
    import important from '@theme/components/important.vue'
</script>

# 常见问题

<important title='注意'>
本页中所有路径均为相对于clickmouse安装目录的路径。
如果windows无法打开里面提到的文件，请尝试用记事本打开。
</important>

## 错误

**1. 语言包不存在：**

请检查clickmouse的`res`目录里是否存在langs目录，如果有，检查里面是否有`langs.json`文件，如果没有，请重新安装clickmouse。[下载链接](https://github.com/xystudiocode/pyclickmouse/releases/latest)

<img class='lang_not_found' alt='语言包不存在' />

**2. 无法启动：**

可能是出现了一些bug，可以在`packages.json`中的内容修改为：
```json
["xystudio.clickmouse", "xystudio.clickmouse.repair"]
```
然后运行当前目录的`repair.exe`文件，勾选你想清除的内容，点击`修复`按钮，再次启动clickmouse看看。

::: tip 提示
推荐全选修复项，但是这样会删除所有用户数据和扩展，恢复到初始状态。
:::

如果你能编译源码，也可以尝试使用makefile，移除编译源码的`--windows-console-mode=disable`获取错误堆栈。

如果仍然不行，可尝试卸载重装clickmouse。[下载链接](https://github.com/xystudiocode/pyclickmouse/releases/latest)

若问题持续，你可以向我们[报告问题](https://github.com/xystudiocode/pyClickMouse/issues/new/choose)

**3. 无法连接到更新，提示`timeout`：**

我们更新内容存放在github上，国内网络较慢。

你可以安装[watt toolkit](https://gitee.com/rmbgame/SteamTools/releases/download/3.0.0-rc.16/Steam%20%20_v3.0.0-rc.16_win_x64.exe)
然后：
1. 打开watt toolkit，点击左侧的`网络加速`
2. 勾选`github`
3. 点击`一键加速`

> 这种方法只能保证不报错timeout，但是不能保证网速快。

如果仍然不行，我也没有更多方法了

## 软件功能使用问题
**1. 为什么连点按钮是灰色的？**

可能是你没有正确的血连点延迟和连点次数，可以在下面的输入框设置连点时间和连点次数，在下拉框中可以选择连点次数/延迟的单位

::: warning 注意
需要填入正确的数字，否则会导致连点失败。
:::

**2. 连点输入框是灰色的/无法打开连点设置**

这可能是你正在连点，需要点击`停止`按钮停止后再次输入。

<img class='input_disable' alt='连点输入框灰色' />
<br />
<img class='stop_click' alt='无法打开连点设置' />

**3. 软件更新失败：更新服务未开启**

请在`设置`，左侧选择`更新`，然后开启`启用更新`

<img class='update_disable' alt='更新服务未开启' />

**4. 提示包管理器文件夹不存在，每次都弹出**

可以前往设置-通知-关闭`官方扩展包丢失警告`

<img class='ipk_not_found' alt='提示包管理器文件夹不存在' />

**5. 选择框点击无效**

你可能点到了文字区域，clickmouse选择框需要点击到框内才有效。


